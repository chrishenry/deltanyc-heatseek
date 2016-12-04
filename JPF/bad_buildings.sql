# v1.0 - JP Freeley - 11/26/2016
#
# SQL - for bad buildings
# Does not account for DATES or TIMES or AGE. 
# Includes by building/address counts of 
#	litigations
#	hpd_violation 'classes'
#	hpd_complaints
#	dob_permits
#	dob_violations
# DOB Data joined by ADDRESS .. not sure if I trust BIN nor BBL
# There are probably more optimal ways to do this.
# !!! Needs better documentation
# !!! Ends up with 2000 MORE BUILDINGS THAN EXIST IN hpd_buildings .. likely dirty addresses .. FIRST()??
### This finds them (1955 rows)
### select hbaddress, buildingid, count(buildingid) count from bad_buildings group by 1,2 having count > 1;


## BELOW REQUIRES THAT NO INDEXES/KEYS PRE-EXIST ON THE TABLES
## AT THE BOTTOM OF THIS FILE IS CODE FOR REMOVING THE FOLLOWING INDEXES/KEYS
alter table hpd_buildings add primary key(buildingid);
alter table hpd_complaintsProb add INDEX(majorcategoryid);
alter table hpd_complaintsProb add INDEX(minorcategoryid);
alter table hpd_complaintsProb add INDEX(codeid);
alter table hpd_complaintsProb add INDEX(complaintid);
alter table hpd_complaints add INDEX(complaintid);
alter table hpd_complaints add INDEX(buildingid);
alter table hpd_violations add INDEX(buildingid);
alter table hpd_violations add index(class);
alter table hpd_registrations add index(buildingid);
alter table hpd_registrations add index(registrationid);
alter table hpd_registrationContact add index(registrationcontactid);
alter table hpd_registrationContact add index(type);
alter table hpd_registrationContact add index(registrationid);
alter table `pubadv_worst_landlords` add index(bin);
alter table pluto_nyc add index(bbl);


delete from dob_violations where boro not in ('1','2','3','4','5');
ALTER TABLE dob_violations CHANGE `boro` `boro` INT(5)  NULL  DEFAULT NULL;
alter table dob_violations add index(boro);

drop table if exists hpd_registrationContact_d;
create temporary table hpd_registrationContact_d 
	select distinct * from hpd_registrationContact;
drop table if exists hpd_registrationContact;
create table hpd_registrationContact select * from hpd_registrationContact_d;
alter table hpd_registrationContact add index(registrationcontactid);
alter table hpd_registrationContact add index(type);
alter table hpd_registrationContact add index(registrationid);

################
drop table if exists boro_lookup;
################
create temporary table boro_lookup select boro, boroid from hpd_buildings group by 1,2;
alter table boro_lookup add index(boroid);

################
drop table if exists hs_complaint_count;
################
create temporary table 
	hs_complaint_count
select	c.buildingid,
	count(*) as count
from 
	hpd_complaintsProb as cp
left join 
	hpd_complaints c
on
	c.complaintid = cp.complaintid
left join 
	hpd_buildings b
on 
	c.buildingid = b.buildingid
where 
	majorcategoryid  in (12, 59, 65) or
	minorcategoryid in (92, 196, 112, 375, 67, 323, 381, 106) or 
	codeid in (800, 801, 802, 803, 804, 809, 1358, 1360, 2713, 2715, 2716, 
	2833, 2490, 605, 616, 617, 629, 634, 640, 801, 1271, 2400, 2532, 2534, 
	2661, 2724, 2764, 2767, 2769, 2794) 
group by 
	1;	
ALTER TABLE `hs_complaint_count` ADD INDEX (`buildingid`);

################
drop table if exists complaint_count;
################
create temporary table complaint_count
select	c.buildingid,
	count(*) as count
from 
	hpd_complaintsProb as cp
left join 
	hpd_complaints c
on
	c.complaintid = cp.complaintid
left outer join 
    hpd_buildings b
on 
   c.buildingid = b.buildingid
group by 
	1;
ALTER TABLE `complaint_count` ADD INDEX (`buildingid`);

################
drop table if exists hpd_complaint_counts;
################
create temporary table 
	hpd_complaint_counts
select 
	concat(trim(hb.housenumber), " ", trim(hb.streetname), " ", trim(hb.boro)) hbaddress,
	concat(boroid,LPAD(hb.block, 5, '0'),LPAD(hb.lot, 4, '0')) bbl,
	hb.buildingid as buildingid, 
	hb.block as block,
	hb.lot as lot,
	hb.bin as bin,
	hb.zip as zip,
	cc.count as all_complaints, 
	hscc.count as hs_complaints
from 
	`hpd_buildings` as hb
left join 
	`hs_complaint_count` hscc
on 
	hb.buildingid = hscc.buildingid
left join
	`complaint_count` cc 
on  
	hb.buildingid = cc.buildingid;
ALTER TABLE `hpd_complaint_counts` ADD INDEX (`buildingid`);
alter table hpd_complaint_counts CHANGE bbl bbl int(12) NULL DEFAULT NULL;
ALTER TABLE `hpd_complaint_counts` ADD INDEX(bbl);
ALTER TABLE `hpd_complaint_counts` ADD INDEX (hbaddress(255));

################
drop table if exists hs_permit_counts;
################
create temporary table hs_permit_counts
select 
	bin_num,
	CONCAT(trim(`house_num`)," ",trim(`street_name`)," ",trim(`borough`)) hs_dobp_address, 
	count(*) hs_permit_cnt
from 
	dob_permits 
where 
	work_type in ("OT","BL", "DM") 
group by 
	1,2;
alter table hs_permit_counts add index(hs_dobp_address(255));
alter table hs_permit_counts add index(bin_num);

################	
drop table if exists permit_counts;
################
create temporary table permit_counts
select 
	bin_num,
	CONCAT(trim(`house_num`)," ",trim(`street_name`)," ",trim(`borough`)) dobp_address, 
	count(*) permit_cnt
from 
	dob_permits 
group by 
	1,2;
alter table permit_counts add index(dobp_address(255));
alter table permit_counts add index(bin_num);

################
drop table if exists violation_counts;
################
create temporary table violation_counts
select 
	bin,
	CONCAT(trim(`house_number`)," ",trim(`street`)," ",trim(bl.boro)) dobv_address, 
	count(*) dob_violation_cnt
from 
	dob_violations dv
left join boro_lookup bl
on dv.boro = bl.boroid
group by 
	1,2;
alter table violation_counts add index(dobv_address(255));
alter table violation_counts add index(bin);

################
drop table if exists classA_vio_cnt;
################
create temporary table classA_vio_cnt
select 
  buildingid,
  count(class) classA_cnt
from 
	hpd_violations
where class = 'A' and currentstatus not in ("VIOLATION DISMISSED", "VIOLATION CLOSED") 
group by 1;
alter table classA_vio_cnt add index(buildingid);

################
drop table if exists classB_vio_cnt;
################
create temporary table classB_vio_cnt
select 
  buildingid,
  count(class) classB_cnt
from 
	hpd_violations
where class = 'B' and currentstatus not in ("VIOLATION DISMISSED", "VIOLATION CLOSED")
group by 1;
alter table classB_vio_cnt add index(buildingid);

################
drop table if exists classC_vio_cnt;
################
create temporary table classC_vio_cnt
select 
  buildingid,
  count(class) classC_cnt
from 
	hpd_violations
where class = 'C' and currentstatus not in ("VIOLATION DISMISSED", "VIOLATION CLOSED")
group by 1;
alter table classC_vio_cnt add index(buildingid);

################
drop table if exists classI_vio_cnt;
################
create temporary table classI_vio_cnt
select 
  buildingid,
  count(class) classI_cnt
from 
	hpd_violations
where class = 'I' and currentstatus not in ("VIOLATION DISMISSED", "VIOLATION CLOSED")
group by 1;
alter table classI_vio_cnt add index(buildingid);

################
drop table if exists lit_count;
################
create temporary table lit_count
select 
	buildingid,
	count(*) lit_cnt
from hpd_litigations
group by 1;
alter table lit_count add index(`buildingid`);

################
drop table if exists hpd_corps;
################
create temporary table hpd_corps
select 
	hrc.registrationcontactid registrationcontactid, 
	hrc.corporationname corporationname, 
	hrc.type type, 
	hr.registrationid registrationid, 
	hr.buildingid buildingid
from 
	hpd_registrations hr
left join 
	hpd_registrationContact hrc on hr.registrationid = hrc.registrationid
where 
	hrc.type = "CorporateOwner";
alter table hpd_corps add index(buildingid);

################
drop table if exists hpd_headOfficers;
################
create temporary table hpd_headOfficers
select 
	hrc.registrationcontactid registrationcontactid, 
	CONCAT(hrc.firstname, " ",hrc.lastname) owner_name, 
	hrc.type type, 
	hr.registrationid registrationid, 
	hr.buildingid buildingid
from 
	hpd_registrationContact hrc
left join 
	hpd_registrations hr on hr.registrationid = hrc.registrationid
where 
	hrc.type = "HeadOfficer";
alter table hpd_headOfficers add index(buildingid);
	

################
################

drop table if exists hpd_complaints_311;

create temporary table hpd_complaints_311
select
	concat(trim(incident_address)," ",trim(borough)) address_311,
	count(*) all_311_hpd_count
from call_311 where agency in ('HPD') and complaint_type not in ('HPD Literature Request') group by 1;

alter table hpd_complaints_311 add index(address_311);

################
################

drop table if exists hpd_heat_complaints_311;

create temporary table hpd_heat_complaints_311
select
	concat(trim(incident_address)," ",trim(borough)) address_311,
	count(*) heat_311_hpd_count
from call_311 
where agency in ('HPD') and complaint_type in ('HEAT/HOT WATER') 
group by 1;

alter table hpd_heat_complaints_311 add index (address_311);

################
################

drop table if exists bad_buildings;

create table bad_buildings
select 
	cc.*, 
	pnyc.council,
	pnyc.ct2010,
	pnyc.cb2010,
	pnyc.numfloors,
	pnyc.unitsres,
	pnyc.unitstotal,
	pnyc.histdist,
	pnyc.xcoord,
	pnyc.ycoord,
	heat_311_hpd_count,
	all_311_hpd_count,
	hs_permit_cnt, 
	permit_cnt,
	dob_violation_cnt,
	cvA.classA_cnt classA_cnt,
	cvB.classB_cnt classB_cnt,
	cvC.classC_cnt classC_cnt,
	cvI.classI_cnt classI_cnt,
	lc.lit_cnt litigation_cnt,
	pawl.officer pa_officer,
	pawl.org pa_org,
	pawl.a pa_hpdv_a_cnt,
	pawl.b pa_hpdv_b_cnt,
	pawl.c pa_hpdv_c_cnt,
	pawl.i pa_hpdv_i_cnt,
	pawl.dob pa_dobv_cnt,
	pawl.units pa_units,
	pawl.score pa_score,
	pawl.lat pa_lat,
	pawl.lng pa_long,
	ho.owner_name owner_name,
	hc.corporationname corp_owner
from 
	hpd_complaint_counts cc
left join 
	hs_permit_counts on hbaddress = hs_dobp_address
left join 
	permit_counts on hbaddress = dobp_address
left join 
	violation_counts on hbaddress = dobv_address
left join 
	pubadv_worst_landlords pawl on cc.bin = pawl.bin
left join
	classA_vio_cnt cvA on cc.buildingid = cvA.buildingid
left join
	classB_vio_cnt cvB on cc.buildingid = cvB.buildingid
left join
	classC_vio_cnt cvC on cc.buildingid = cvC.buildingid
left join
	classI_vio_cnt cvI on cc.buildingid = cvI.buildingid
left join
	lit_count lc on cc.buildingid = lc.buildingid
left join
	hpd_heat_complaints_311 hhc3 on hbaddress = hhc3.address_311
left join
	hpd_complaints_311 hc3 on hbaddress = hc3.address_311
left join
	pluto_nyc pnyc on cc.bbl = pnyc.bbl
left join 
	hpd_headOfficers ho on cc.buildingid = ho.buildingid
left join 
	hpd_corps hc on cc.buildingid = hc.buildingid
		;

## DROP ALL KEYS AND CHANGES TO ORIGINAL TABLES RUN FAR ABOVE
alter table hpd_buildings drop primary key;
alter table hpd_complaintsProb DROP INDEX majorcategoryid;
alter table hpd_complaintsProb drop INDEX minorcategoryid;
alter table hpd_complaintsProb drop INDEX codeid;
alter table hpd_complaintsProb drop INDEX complaintid;
alter table hpd_complaints drop INDEX complaintid;
alter table hpd_complaints drop INDEX buildingid;
alter table hpd_violations drop INDEX buildingid;
alter table hpd_violations drop index class;
alter table hpd_registrations drop index buildingid;
alter table hpd_registrations drop index registrationid;
alter table hpd_registrationContact drop index registrationcontactid;
alter table hpd_registrationContact drop index registrationid;
alter table dob_violations drop index boro;
alter table `pubadv_worst_landlords` drop index bin;

select * from bad_buildings limit 100;


### FIND LANDLORDS
-- alter table hpd_buildings add index(bin);
-- alter table `pubadv_worst_landlords` add index(bin);
-- alter table hpd_registrations add index(buildingid);
-- alter table hpd_registrations add index(registrationid);
-- alter table hpd_registrationContact add index(registrationid);

-- select * from hpd_buildings hb 
-- join pubadv_worst_landlords pawl on hb.bin = pawl.bin
-- join hpd_registrations hr on hb.buildingid = hr.buildingid
-- join hpd_registrationContact hrc on hr.registrationid = hrc.registrationid 
-- where hrc.type in ("HeadOfficer", "CorporateOwner");

-- alter table hpd_buildings drop index bin;
-- alter table `pubadv_worst_landlords` drop index bin;
-- alter table hpd_registrations drop index buildingid ;
-- alter table hpd_registrations DROP index registrationid ;
-- alter table hpd_registrationContact drop index registrationid;


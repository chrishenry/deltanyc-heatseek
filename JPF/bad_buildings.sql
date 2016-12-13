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
alter table hpd_buildings add index(lifecycle);
alter table hpd_buildings add index(bin);
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
alter table pubadv_worst_landlords add index(bin);
alter table pluto_nyc add index(bbl);
alter table tb_changes_summary add index(ucbbl);
alter table hpd_aep_list add index(full_addr);

delete from hpd_buildings where buildingid = 814731; #FICTICIOUS?? OVERSIZED BBL .. DELETE

delete from dob_violations where boro not in ('1','2','3','4','5');
ALTER TABLE dob_violations CHANGE `boro` `boro` INT(5)  NULL  DEFAULT NULL;
alter table dob_violations add index(boro);
alter table dob_violations add index(bin);
alter table dob_permits add index (borough);

delete from dob_violations 
where 
	bin < 1000000 or 
	bin > 5999999 or 
	bin = 1000000 or 
	bin = 2000000 or 
	bin = 3000000 or 
	bin = 4000000 or 
	bin = 5000000;
	
delete from hpd_buildings 
where 
	bin < 1000000 or 
	bin > 5999999 or 
	bin = 1000000 or 
	bin = 2000000 or 
	bin = 3000000 or 
	bin = 4000000 or 
	bin = 5000000;

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
alter table boro_lookup add index(boro);

################
drop table if exists hpd_buildings_temp;
################

create temporary table
	hpd_buildings_temp
select * from hpd_buildings where lifecycle = 'Building';
alter table hpd_buildings_temp add primary key(buildingid);

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
	hpd_buildings_temp b
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
    hpd_buildings_temp b
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
	concat(trim(boroid),trim(LPAD(hb.block, 5, '0')),trim(LPAD(hb.lot, 4, '0'))) bbl,
	hb.buildingid as buildingid, 
	hb.block as block,
	hb.lot as lot,
	hb.bin as bin,
	hb.zip as zip,
	cc.count as all_hpd_complaints, 
	hscc.count as hs_hpd_complaints
from 
	hpd_buildings_temp as hb
left join 
	`hs_complaint_count` hscc
on 
	hb.buildingid = hscc.buildingid
left join
	`complaint_count` cc 
on  
	hb.buildingid = cc.buildingid
;
ALTER TABLE `hpd_complaint_counts` ADD INDEX (`buildingid`);
ALTER TABLE `hpd_complaint_counts` ADD INDEX (bin);
alter table hpd_complaint_counts CHANGE bbl bbl bigint(13) NULL DEFAULT NULL;
ALTER TABLE `hpd_complaint_counts` ADD INDEX(bbl);
ALTER TABLE `hpd_complaint_counts` ADD INDEX (hbaddress(255));

################
drop table if exists hs_permit_counts;
################
create temporary table hs_permit_counts
select 
	bin_num bin,
#	CONCAT(trim(`house_num`)," ",trim(`street_name`)," ",trim(`borough`)) address, 
#   concat(trim(bl.boroid),trim(LPAD(dp.block, 5, '0')),trim(LPAD(dp.lot, 4, '0'))) bbl,
	count(*) hs_permit_cnt
from 
	dob_permits dp
left join boro_lookup bl on bl.boro = dp.borough
where 
	work_type in ("OT","BL", "DM") 
group by 
	1;
#alter table hs_permit_counts add index(address(255));
alter table hs_permit_counts add index(bin);
#alter table hs_permit_counts add index(bbl);

################	
drop table if exists permit_counts;
################
create temporary table permit_counts
select 
	bin_num bin,
#	CONCAT(trim(`house_num`)," ",trim(`street_name`)," ",trim(`borough`)) address, 
#	concat(trim(bl.boroid),trim(LPAD(dp.block, 5, '0')),trim(LPAD(dp.lot, 4, '0'))) bbl,
	count(*) permit_cnt
from 
	dob_permits dp
left join boro_lookup bl on bl.boro = dp.borough
group by 
	1;
#alter table permit_counts add index(address(255));
alter table permit_counts add index(bin);
#alter table permit_counts add index(bbl);


################
drop table if exists violation_counts;
################
create temporary table violation_counts
select 
	bin,
	#CONCAT(trim(`house_number`)," ",trim(`street`)," ",trim(bl.boro)) address, 
	#concat(trim(bl.boroid),trim(LPAD(block, 5, '0')),trim(LPAD(lot, 4, '0'))) bbl,
	count(*) dob_violation_cnt
from 
	dob_violations dv
left join 
	boro_lookup bl on dv.boro = bl.boroid
where 
	`violation_category` not like ("%dismissed%") and	`violation_category` not like ("%resolved%")
group by 
	1;
#alter table violation_counts add index(address(255));
alter table violation_counts add index(bin);
#alter table violation_counts add index(bbl);
#DELETE FROM violation_counts where bbl like "% %";
#delete from violation_counts where bbl like "%N%";
#delete from violation_counts where bbl regexp '[A-Za-z]';


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
from call_311 where agency in ('HPD') and complaint_type not in ('HPD Literature Request') 
group by 1;

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

drop table if exists hpd_pluto;

create temporary table hpd_pluto
select
	cc.buildingid,
	pnyc.unitstotal, 
	pnyc.unitsres
from 
	hpd_complaint_counts cc
left join
	pluto_nyc pnyc on pnyc.bbl = cc.bbl
;
#where agency in ('HPD') and complaint_type in ('HEAT/HOT WATER') 
#group by 1;

#alter table hpd_heat_complaints_311 add index (address_311);

################
################

drop table if exists aep_2008;
drop table if exists aep_2009;
drop table if exists aep_2010;
drop table if exists aep_2011;
drop table if exists aep_2012;
drop table if exists aep_2013;
drop table if exists aep_2014;
drop table if exists aep_2015;
drop table if exists aep_2016; 
create temporary table aep_2008 select * from hpd_aep_list where year = 2008;
create temporary table aep_2009 select * from hpd_aep_list where year = 2009;
create temporary table aep_2010 select * from hpd_aep_list where year = 2010;
create temporary table aep_2011 select * from hpd_aep_list where year = 2011;
create temporary table aep_2012 select * from hpd_aep_list where year = 2012;
create temporary table aep_2013 select * from hpd_aep_list where year = 2013;
create temporary table aep_2014 select * from hpd_aep_list where year = 2014;
create temporary table aep_2015 select * from hpd_aep_list where year = 2015;
create temporary table aep_2016 select * from hpd_aep_list where year = 2016;
alter table aep_2008 add index(full_addr);
alter table aep_2009 add index(full_addr);
alter table aep_2010 add index(full_addr);
alter table aep_2011 add index(full_addr);
alter table aep_2012 add index(full_addr);
alter table aep_2013 add index(full_addr);
alter table aep_2014 add index(full_addr);
alter table aep_2015 add index(full_addr);
alter table aep_2016 add index(full_addr);

################
################

drop table if exists bad_buildings;

create table bad_buildings
select 
	cc.hbaddress,
	cc.bbl,
	cc.buildingid,
	cc.block,
	cc.lot,
	cc.bin,
	cc.zip,
	cc.all_hpd_complaints,
	cc.hs_hpd_complaints, 
	heat_311_hpd_count,
	all_311_hpd_count,
	dob_violation_cnt,
	permit_cnt,
	hs_permit_cnt,
	if (pnyc.unitsres != 0, (cc.all_hpd_complaints / pnyc.unitsres) ,0) all_hpd_complaints_per_resunits,
	if (pnyc.unitsres != 0, (cc.hs_hpd_complaints / pnyc.unitsres) ,0) hs_hpd_complaints_per_resunits,
	if (pnyc.unitsres != 0, (heat_311_hpd_count / pnyc.unitsres) ,0) heat_311_hpd_count_per_resunits,
	if (pnyc.unitsres != 0, (all_311_hpd_count / pnyc.unitsres) ,0) all_311_hpd_count_per_resunits,
	if (pnyc.unitsres != 0, (dob_violation_cnt / pnyc.unitsres) ,0) dob_violation_cnt_per_resunits,
	if (pnyc.unitsres != 0, (hs_permit_cnt / pnyc.unitsres) ,0) hs_permit_cnt_per_resunits,
	if (pnyc.unitsres != 0, (tbcs.unitsstab2007 / pnyc.unitsres) ,0) rentstab2007_per_resunits,
	if (pnyc.unitsres != 0, (tbcs.unitsstab2015 / pnyc.unitsres) ,0) rentstab2015_per_resunits,
	if (pnyc.unitsres != 0, (tbcs.diff / pnyc.unitsres) ,0)  diff_per_resunits, 
	if (pnyc.unitsres != 0, (cvA.classA_cnt / pnyc.unitsres) ,0)  classA_cnt_per_resunits, 
	if (pnyc.unitsres != 0, (cvB.classB_cnt / pnyc.unitsres) ,0)  classB_cnt_per_resunits, 
	if (pnyc.unitsres != 0, (cvC.classC_cnt / pnyc.unitsres) ,0)  classC_cnt_per_resunits, 
	if (pnyc.unitsres != 0, (cvI.classI_cnt / pnyc.unitsres) ,0)  classI_cnt_per_resunits, 		
	if (pnyc.unitsres != 0, (lc.lit_cnt / pnyc.unitsres) ,0)  lit_cnt_per_resunits, 			
	if (pnyc.unitsres != 0, (pawl.dob_hpd / pnyc.unitsres) ,0) pa_dob_hpd_cnt_per_resunits, 			
	if (a08.year = 2008,1,0) aep08,
	if (a09.year = 2009,1,0) aep09,
	if (a10.year = 2010,1,0) aep10,
	if (a11.year = 2011,1,0) aep11,
	if (a12.year = 2012,1,0) aep12,
	if (a13.year = 2013,1,0) aep13,
	if (a14.year = 2014,1,0) aep14,
	if (a15.year = 2015,1,0) aep15,
	if (a16.year = 2016,1,0) aep16,
	(
	if (a08.year = 2008,1,0)+
	if (a09.year = 2009,1,0)+
	if (a10.year = 2010,1,0)+
	if (a11.year = 2011,1,0)+
	if (a12.year = 2012,1,0)+
	if (a13.year = 2013,1,0)+
	if (a14.year = 2014,1,0)+
	if (a15.year = 2015,1,0)+
	if (a16.year = 2016,1,0)
	) as total_aep_yrs,
	pnyc.council,
	pnyc.ct2010,
	pnyc.cb2010,
	pnyc.numfloors,
	pnyc.unitsres,
	pnyc.unitstotal,
	pnyc.histdist,
	pnyc.xcoord,
	pnyc.ycoord,
	tbcs.unitsstab2007,
	tbcs.unitsstab2015,
	tbcs.diff, 
	tbcs.percentchange,
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
	pawl.dob_hpd pa_dobhpd_cnt,
	pawl.units pa_units,
	pawl.score pa_score,
	pawl.lat pa_lat,
	pawl.lng pa_long,
	ho.owner_name owner_name,
	hc.corporationname corp_owner,
	hb.managementprogram
from 
	hpd_complaint_counts cc
left join 
	hs_permit_counts hpc on hpc.bin = cc.bin ## DO NOT USE BBL .. QUERY HANGS
left join 
	permit_counts pc on pc.bin = cc.bin      ## DO NOT USE BBL .. QUERY HANGS
left join 
	violation_counts vc on vc.bin = cc.bin   ## DO NOT USE BBL .. QUERY HANGS
left join 
	pubadv_worst_landlords pawl on pawl.bin = cc.bin
left join
	classA_vio_cnt cvA on cvA.buildingid = cc.buildingid
left join
	classB_vio_cnt cvB on cvB.buildingid = cc.buildingid
left join
	classC_vio_cnt cvC on cvC.buildingid = cc.buildingid
left join
	classI_vio_cnt cvI on cvI.buildingid = cc.buildingid
left join
	lit_count lc on lc.buildingid = cc.buildingid
left join
	hpd_heat_complaints_311 hhc3 on (hhc3.address_311) = (hbaddress)
left join
	hpd_complaints_311 hc3 on (hc3.address_311) = (hbaddress)
left join
	pluto_nyc pnyc on pnyc.bbl = cc.bbl
left join 
	hpd_headOfficers ho on ho.buildingid = cc.buildingid
left join 
	hpd_corps hc on hc.buildingid = cc.buildingid
left join
	tb_changes_summary tbcs on tbcs.ucbbl = cc.bbl 
left join
	aep_2008 a08 on (a08.full_addr) = (hbaddress)
left join
	aep_2009 a09 on (a09.full_addr) = (hbaddress)
left join
	aep_2010 a10 on (a10.full_addr) = (hbaddress)
left join
	aep_2011 a11 on (a11.full_addr) = (hbaddress)
left join
	aep_2012 a12 on (a12.full_addr) = (hbaddress)
left join
	aep_2013 a13 on (a13.full_addr) = (hbaddress)
left join
	aep_2014 a14 on (a14.full_addr) = (hbaddress)
left join
	aep_2015 a15 on (a15.full_addr) = (hbaddress)		
left join
	aep_2016 a16 on (a16.full_addr) = (hbaddress)
left join
	hpd_buildings_temp hb on hb.buildingid = cc.buildingid
;

## CREATE AND SET THE TARGET COLUMN
ALTER TABLE bad_buildings ADD `target` INT  NULL  DEFAULT NULL  AFTER `managementprogram`;
ALTER TABLE bad_buildings ADD `bb_target` INT  NULL  DEFAULT NULL  AFTER `target`;
ALTER TABLE bad_buildings ADD `bb_score` FLOAT  NULL  DEFAULT NULL  AFTER `bb_target`;
alter table bad_buildings add index(unitsres);
alter table bad_buildings add index(pa_score);
alter table bad_buildings add index(dob_violation_cnt);
alter table bad_buildings add index(total_aep_yrs);

update bad_buildings set classB_cnt = 0 where classB_cnt is null;
update bad_buildings set classC_cnt = 0 where classC_cnt is null;
update bad_buildings set dob_violation_cnt = 0 where dob_violation_cnt is null;
update bad_buildings set target = null;
update bad_buildings set target = 1 where pa_score is not null or total_aep_yrs > 0;
alter table bad_buildings add index(target);
update bad_buildings set bb_score = null;
update bad_buildings set bb_score = ((`dob_violation_cnt`* 2) + (`classC_cnt`*1.5) + `classB_cnt`)/`unitsres` where unitsres > 0;
alter table bad_buildings add index(bb_score);
update bad_buildings set bb_target = NULL;
update bad_buildings set bb_target = 0 where bb_score is not null;
update bad_buildings set bb_target = 1 where bb_score >= 2 and unitsres >= 35 ;
update bad_buildings set bb_target = 1 where bb_score >= 3 and unitsres < 35 ;
alter table bad_buildings add index(bb_target);


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
alter table pubadv_worst_landlords drop index bin;
alter table pluto_nyc drop index bbl;
alter table tb_changes_summary drop index ucbbl;
alter table hpd_aep_list drop index full_addr;

select * from bad_buildings limit 100;

select * from bad_buildings where target = 1;


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

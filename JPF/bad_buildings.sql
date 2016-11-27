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


delete from dob_violations where boro not in ('1','2','3','4','5');
ALTER TABLE `dob_violations` CHANGE `boro` `boro` INT(5)  NULL  DEFAULT NULL;
alter table dob_violations add index(boro);

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
	hb.buildingid as buildingid, 
	hb.block as block,
	hb.lot as lot,
	hb.bin as bin,
	hb.zip as zip
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

################
drop table if exists classA_vio_cnt;
################
create temporary table classA_vio_cnt
select 
  buildingid,
  count(class) classA_cnt
from 
	hpd_violations
where class = 'A'
group by 1;

################
drop table if exists classB_vio_cnt;
################
create temporary table classB_vio_cnt
select 
  buildingid,
  count(class) classB_cnt
from 
	hpd_violations
where class = 'B'
group by 1;

################
drop table if exists classC_vio_cnt;
################
create temporary table classC_vio_cnt
select 
  buildingid,
  count(class) classC_cnt
from 
	hpd_violations
where class = 'C'
group by 1;

################
drop table if exists classI_vio_cnt;
################
create temporary table classI_vio_cnt
select 
  buildingid,
  count(class) classI_cnt
from 
	hpd_violations
where class = 'I'
group by 1;

################
drop table if exists lit_count;
################
create temporary table lit_count
select 
	buildingid,
	count(*) lit_cnt
from hpd_litigations
group by 1;
alter table lit_count add index(`buildingid`)	;
	
################
ALTER TABLE `hpd_complaint_counts` ADD INDEX (`hbaddress`(255)); 
ALTER TABLE `hs_permit_counts` ADD INDEX (`hs_dobp_address`(255)); 
ALTER TABLE `permit_counts` ADD INDEX (`dobp_address`(255)); 
ALTER TABLE `violation_counts` ADD INDEX (`dobv_address`(255)); 
alter table classA_vio_cnt add index(buildingid);
alter table classB_vio_cnt add index(buildingid);
alter table classC_vio_cnt add index(buildingid);
alter table classI_vio_cnt add index(buildingid);
################

################
drop table if exists bad_buildings;
################
create temporary table bad_buildings
select 
	cc.*, 
	hs_permit_cnt, 
	permit_cnt,
	dob_violation_cnt,
	cvA.classA_cnt,
	cvB.classB_cnt,
	cvC.classC_cnt,
	cvI.classI_cnt,
	lc.lit_cnt,
	landlord pa_landlord,
	hpdv pa_hpdv,
	dobv pa_dobv
from 
	`hpd_complaint_counts` cc
left join 
	hs_permit_counts on `hbaddress` = hs_dobp_address
left join 
	permit_counts on `hbaddress` = dobp_address
left join 
	violation_counts on `hbaddress` = dobv_address
left join 
	`pubadv_worst_landlords` on `hbaddress` = `ADDR`
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

delete from dob_violations where boro not in ('1','2','3','4','5');
ALTER TABLE `dob_violations` CHANGE `boro` `boro` INT(5)  NULL  DEFAULT NULL;
alter table dob_violations drop index boro;


select * from bad_buildings limit 100;


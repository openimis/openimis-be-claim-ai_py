import numpy
import pandas

from django.db import connection, ProgrammingError

from core import datetime


class RawSQLDataFrameLoader:
    __BASE_SQL = """drop table if exists #claimsForEvaluation;

select * into #claimsForEvaluation from 
(select distinct 
			tci.ClaimItemID as 'ProvisionID', 
			Cast('Medication' as VARCHAR(50)) as 'ProvisionType',   
			ti.ItemUUID as 'ItemUUID',
			th.HfUUID as 'HFUUID', 
			tl.LocationId as 'LocationId',
			(select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID = ti2.ICDID) as 'ICDCode',
			coalesce ((select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID1 = ti2.ICDID), NULL) as 'ICD1Code',
			tp.ProdID as 'ProdID', 
			ins.DOB as 'DOB',
			tg.Code as 'Gender', 
			tf.Poverty as 'Poverty',
			CAST(tci.QtyProvided AS INT) as 'QuantityProvided',
			ti.ItemPrice as 'ItemPrice', 
			tci.PriceAsked as 'PriceAsked',
			coalesce(tc.DateFrom, tc.DateTo) as 'DateFrom',
			tc.DateTo as 'DateTo',
			tc.DateClaimed as 'DateClaimed',
			ti.ItemFrequency as 'ItemFrequency',
			ti.ItemPatCat as 'ItemPatCat',
			'M' as 'ItemLevel',
			th.HFLevel as 'HFLevel',
			th.HFCareType as 'HFCareType',
			tc.VisitType as 'VisitType',
			tci.RejectionReason as 'RejectionReason',
			tci.PriceValuated as 'PriceValuated',
			(select HfUUID  from tblHF where HfID = tca.HFId) as 'HfUUID1',
			tca.ClaimAdminUUID as 'ClaimAdminUUID',
			ins.InsureeUUID as 'InsureeUUID',
			tc.ClaimUUID as 'ClaimUUID',
			'new' as 'New'
		from tblClaimItems tci 
		left join tblClaim tc on tci.ClaimID = tc.ClaimID
		left join tblHF th on tc.HFID = th.HfID 
		left join tblLocations tl on th.LocationId = tl.LocationId 
		left join tblICDCodes td on (tc.ICDID = td.ICDID or tc.ICDID1 = td.ICDID)
		left join tblItems ti on tci.ItemID = ti.ItemID   
		left join tblProduct tp on tci.ProdID = tp.ProdID 
		left join tblInsuree ins on ins.InsureeID = tc.InsureeID 
		left join tblFamilies tf on ins.FamilyID = tf.FamilyID
		left join tblGender tg on tg.Code = ins.Gender  
		left join tblClaimAdmin tca on tca.ClaimAdminId = tc.ClaimAdminId 
		where tci.ClaimID in (__CLAIM_ID_PLACEHOLDER__) and tci.ValidityTo is null)x;
	
insert into #claimsForEvaluation select * from (
select 
		tci.ClaimServiceID  as 'ProvisionID', 
		'ActivityDefinition' as 'ProvisionType',   
		ti.ServiceUUID  as 'ItemUUID',
		th.HfUUID as 'HFUUID', 
		tl.LocationId as 'LocationId',
		(select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID = ti2.ICDID) as 'ICDCode',
		coalesce ((select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID1 = ti2.ICDID), NULL) as 'ICD1Code',
		tp.ProdID as 'ProdID', 
		ins.DOB as 'DOB',
		tg.Code as 'Gender', 
		tf.Poverty as 'Poverty',
		CAST(tci.QtyProvided AS INT) as 'QuantityProvided',
		ti.ServPrice  as 'ItemPrice', 
		tci.PriceAsked as 'PriceAsked',
		coalesce(tc.DateFrom, tc.DateTo) as 'DateFrom',
		tc.DateTo as 'DateTo',
		tc.DateClaimed as 'DateClaimed',
		ti.ServFrequency  as 'ItemFrequency',
		ti.ServPatCat  as 'ItemPatCat',
		ti.ServLevel  as 'ItemLevel',
		th.HFLevel as 'HFLevel',
		th.HFCareType as 'HFCareType',
		tc.VisitType as 'VisitType',
		tci.RejectionReason as 'RejectionReason',
		tci.PriceValuated as 'PriceValuated',
		(select HfUUID  from tblHF where HfID = tca.HFId) as 'HfUUID1',
		tca.ClaimAdminUUID as 'ClaimAdminUUID',
		ins.InsureeUUID as 'InsureeUUID',
		tc.ClaimUUID as 'ClaimUUID',
		'new' as 'New'
	from tblClaimServices tci 
	left join tblClaim tc on tci.ClaimID = tc.ClaimID
	left join tblHF th on tc.HFID = th.HfID 
	left join tblLocations tl on th.LocationId = tl.LocationId 
	left join tblICDCodes td on (tc.ICDID = td.ICDID or tc.ICDID1 = td.ICDID)
	left join tblServices ti on tci.ServiceID  = ti.ServiceID   
	left join tblProduct tp on tci.ProdID = tp.ProdID 
	left join tblInsuree ins on ins.InsureeID = tc.InsureeID 
	left join tblFamilies tf on ins.FamilyID = tf.FamilyID
	left join tblGender tg on tg.Code = ins.Gender  
	left join tblClaimAdmin tca on tca.ClaimAdminId = tc.ClaimAdminId 
	where tci.ClaimID in (__CLAIM_ID_PLACEHOLDER__))x;

insert into #claimsForEvaluation select * from (
select distinct
		tci.ClaimItemID as 'ProvisionID', 
		'Medication' as 'ProvisionType',   
		ti.ItemUUID as 'ItemUUID',
		th.HfUUID as 'HFUUID', 
		tl.LocationId as 'LocationId',
		(select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID = ti2.ICDID) as 'ICDCode',
		coalesce ((select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID1 = ti2.ICDID), NULL) as 'ICD1Code',
		tp.ProdID as 'ProdID', 
		ins.DOB as 'DOB',
		tg.Code as 'Gender', 
		tf.Poverty as 'Poverty',
		CAST(tci.QtyProvided AS INT) as 'QuantityProvided',
		ti.ItemPrice as 'ItemPrice', 
		tci.PriceAsked as 'PriceAsked',
		coalesce(tc.DateFrom, tc.DateTo) as 'DateFrom',
		tc.DateTo as 'DateTo',
		tc.DateClaimed as 'DateClaimed',
		ti.ItemFrequency as 'ItemFrequency',
		ti.ItemPatCat as 'ItemPatCat',
		'M' as 'ItemLevel',
		th.HFLevel as 'HFLevel',
		th.HFCareType as 'HFCareType',
		tc.VisitType as 'VisitType',
		tci.RejectionReason as 'RejectionReason',
		tci.PriceValuated as 'PriceValuated',
		(select HfUUID  from tblHF where HfID = tca.HFId) as 'HfUUID1',
		tca.ClaimAdminUUID as 'ClaimAdminUUID',
		ins.InsureeUUID as 'InsureeUUID',
		tc.ClaimUUID as 'ClaimUUID',
		'old' as 'New'
	from tblClaimItems tci 
	left join tblClaim tc on tci.ClaimID = tc.ClaimID
	left join tblHF th on tc.HFID = th.HfID 
	left join tblLocations tl on th.LocationId = tl.LocationId 
	left join tblICDCodes td on (tc.ICDID = td.ICDID or tc.ICDID1 = td.ICDID)
	left join tblItems ti on tci.ItemID = ti.ItemID   
	left join tblProduct tp on tci.ProdID = tp.ProdID 
	left join tblInsuree ins on ins.InsureeID = tc.InsureeID 
	left join tblFamilies tf on ins.FamilyID = tf.FamilyID
	left join tblGender tg on tg.Code = ins.Gender  
	left join tblClaimAdmin tca on tca.ClaimAdminId = tc.ClaimAdminId 
where tci.ValidityTo is null and (
	  ins.InsureeUUID in (select InsureeUUID from #claimsForEvaluation where ProvisionType = 'Medication') 
	or 
	  th.HfUUID in (select HFUUID from #claimsForEvaluation where ProvisionType = 'Medication')
) and tci.ClaimItemID not in (select ProvisionID from #claimsForEvaluation where ProvisionType = 'Medication'))x;


insert into #claimsForEvaluation select * from (
select distinct
		tci.ClaimServiceID  as 'ProvisionID', 
		'ActivityDefinition' as 'ProvisionType',   
		ti.ServiceUUID  as 'ItemUUID',
		th.HfUUID as 'HFUUID', 
		tl.LocationId as 'LocationId',
		(select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID = ti2.ICDID) as 'ICDCode',
		coalesce ((select ti2.ICDCode  from tblICDCodes ti2 where tc.ICDID1 = ti2.ICDID), NULL) as 'ICD1Code',
		tp.ProdID as 'ProdID', 
		ins.DOB as 'DOB',
		tg.Code as 'Gender', 
		tf.Poverty as 'Poverty',
		CAST(tci.QtyProvided AS INT) as 'QuantityProvided',
		ti.ServPrice  as 'ItemPrice', 
		tci.PriceAsked as 'PriceAsked',
		coalesce(tc.DateFrom, tc.DateTo) as 'DateFrom',
		tc.DateTo as 'DateTo',
		tc.DateClaimed as 'DateClaimed',
		ti.ServFrequency  as 'ItemFrequency',
		ti.ServPatCat  as 'ItemPatCat',
		ti.ServLevel  as 'ItemLevel',
		th.HFLevel as 'HFLevel',
		th.HFCareType as 'HFCareType',
		tc.VisitType as 'VisitType',
		tci.RejectionReason as 'RejectionReason',
		tci.PriceValuated as 'PriceValuated',
		(select HfUUID  from tblHF where HfID = tca.HFId) as 'HfUUID1',
		tca.ClaimAdminUUID as 'ClaimAdminUUID',
		ins.InsureeUUID as 'InsureeUUID',
		tc.ClaimUUID as 'ClaimUUID',
		'old' as 'New'
	from tblClaimServices tci 
	left join tblClaim tc on tci.ClaimID = tc.ClaimID
	left join tblHF th on tc.HFID = th.HfID 
	left join tblLocations tl on th.LocationId = tl.LocationId 
	left join tblICDCodes td on (tc.ICDID = td.ICDID or tc.ICDID1 = td.ICDID)
	left join tblServices ti on tci.ServiceID  = ti.ServiceID   
	left join tblProduct tp on tci.ProdID = tp.ProdID 
	left join tblInsuree ins on ins.InsureeID = tc.InsureeID 
	left join tblFamilies tf on ins.FamilyID = tf.FamilyID
	left join tblGender tg on tg.Code = ins.Gender  
	left join tblClaimAdmin tca on tca.ClaimAdminId = tc.ClaimAdminId
where tci.ValidityTo is null and (
	  ins.InsureeUUID in (select InsureeUUID from #claimsForEvaluation where ProvisionType = 'ActivityDefinition') 
	or 
	  th.HfUUID in (select HFUUID from #claimsForEvaluation)
) and tci.ClaimServiceID not in (select ProvisionID from #claimsForEvaluation where ProvisionType = 'ActivityDefinition'))x;

"""

    __SELECT_SQL = """select * from #claimsForEvaluation;"""

    @classmethod
    def build_dataframe_for_claim_ids(cls, claim_ids):
        s = ", ".join(map(lambda x: "%s", claim_ids))
        y = cls.__BASE_SQL.replace("__CLAIM_ID_PLACEHOLDER__", s)
        query = y % (*claim_ids, *claim_ids)

        cursor = connection.cursor()
        cursor.execute(query)
        while cursor.nextset():
            try:
                cursor.fetchall()
            except ProgrammingError as e:
                # Sql was not a query but it's required to call fetchall(), in other case read_sql fails
                pass
            continue

        df = pandas.read_sql_query(cls.__SELECT_SQL, con=connection)
        df.rename(columns={'HfUUID1': 'HfUUID'}, inplace=True)
        cursor.close()
        df['DateClaimed'] = df['DateClaimed'].map(lambda x: datetime.date(x.year, x.month, x.day))
        df['DateFrom'] = df['DateFrom'].map(lambda x: datetime.date(x.year, x.month, x.day))
        df['DateTo'] = df['DateTo'].map(lambda x: datetime.date(x.year, x.month, x.day) if x else None)
        df['DateTo'] = numpy.where(~df['DateTo'].isnull(), df['DateTo'], df['DateFrom'])
        df['DOB'] = df['DOB'].map(lambda x: datetime.date(x.year, x.month, x.day))
        return df

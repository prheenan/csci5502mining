# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
# need to add the utilities class. Want 'home' to be platform independent
from os.path import expanduser
home = expanduser("~")
# get the utilties directory (assume it lives in ~/utilities/python)
# but simple to change
path= home +"/utilities/python"
import sys
sys.path.append(path)
# import the patrick-specific utilities
import GenUtilities  as pGenUtil
import PlotUtilities as pPlotUtil
import CheckpointUtilities as pCheckUtil
import datetime
# Import a model for default use...
from ReaderModel.HighBandwidthFoldUnfold import HighBandwidthModel

SQL_BOOT_CYPHER_DEF_SAMPLE_PREP = 1
SQL_BOOT_CYPHER_DEF_SAMPLE_TYPE = 1
SQL_BOOT_CYPHER_LONG = 1
SQL_BOOT_CYPHER_FIBMINI = 4
import SqlDataModel
from PyUtil import SqlUtil

def AddDefaultTipTypes(sess,mCls):
    # Add the tip types
    Names = ["Biolever_Long","Biolever_Mini","BioLever_Fast",
             "FIB_Biolever_Fast","FIB_BioLever_Mini"]
    Descriptions = ["Standard Olympus Biolever Long",
                    "Standard Olympus Biolever Mini",
                    "Standard Olympus Biolevel Fast",
                    "Focused Ion Beam Modified Biolever Fast",
                    "Focused Ion Beam Modified Biolevel Mini"]  
    nTypes = len(Names)
    i=0
    for i in range(nTypes):
        # POST: tmp is set up with the type and descriptions needed
        TipType = mCls.TipType(Name=Names[i],Description=Descriptions[i])
        SqlDataModel.Insert(sess,TipType)
                            

def AddDefaultMolecules(sess,mCls):
    # Add the families, molecule types, and samples
    FamilyNames = ["DNA","RNA","Protein"]
    Descriptions = ["Deoxyribonucleic acid",
                    "Oxyribonucleic acid",
                    "A Polypeptide"]
    dnaIndex = 0
    nFamilies = len(FamilyNames)
    for i in range(nFamilies):
        mFam = mCls.MoleculeFamily(Name=FamilyNames[i],
                                   Description=Descriptions[i])
        SqlDataModel.Insert(sess,mFam)
        # XXX magic number; 1 is the first thing in the database
        # add in the molecule type
        Description= "Mp13 plasmid with 1607F-DBCO and 3520R-Bio" +\
                     "primers with 12 nt complementary overhang: "+\
                     "GTG GTC CTA GTG"
    mFam = mCls.MolType(idMoleculeFamily = 1,
                        Name="CircularDNA",
                        Description=Description,
                        MolMass=0)
    SqlDataModel.Insert(sess,mFam)

def AddDefaultRatings(sess,mCls):
    Ratings = [-1,1,2,3,4,5]
    Names = ["Unrated","Very Low Quality, very high noise",
             "Low Quality or high noise","Standard","Great",
             "Paper-or Talk-Worthy"]
    for rate,name in zip(Ratings,Names):
        # note that descriptions are the same as the names...
        SqlDataModel.Insert(sess,mCls.TraceRating(RatingValue=rate,
                                                  Name=name,
                                                  Description=name))

def AddDefaultUsers(sess,mCls):
    Names = ["Patrick_Heenan","William_'John'_Van_Patten","Devin_Edwards",
             "Thomas_Perkins"]
    for n in Names:
        SqlDataModel.Insert(sess,mCls.User(Name=n))
    
def AddDefaultSamplePreps(sess,mCls):
    Name =["Standard_GelPurified"]
    Description = ["Amplified DNA, purified by gel electrophoresis," +\
                   "Bio-Rad Quantum freeze and squeeze, and (optionally)" +\
                   "Amicon 10K 0.5mL"]
    for n,desc in zip(Name,Description):
        SqlDataModel.Insert(sess,mCls.SamplePrep(Name=Name,
                                                 Description=Description))

def AddDefaultTipPreps(sess,mCls):
    Description = "Standard As Of 2015/07"
    GoldEtchSec = 30
    ChromEtchSec = 30
    SqlDataModel.Insert(sess,mCls.TipPrep(Description=Description,
                                          Name="Standard",
                                          SecondsEtchGold=GoldEtchSec,
                                          SecondsEtchChromium=ChromEtchSec))

def AddDefaultTipPack(sess,mCls):
    Name = "Unknown"
    Description  = "Unkown Tip Pack"
    SqlDataModel.Insert(sess,mCls.TipPack(Name=Name,Description=Description))

# Add the samples already made.
def AddDefaultSamples(sess,mCls):		
    DateSampleCreated = ["2015/6/04","2015/6/04","2015/6/30"]
    DateSampleDeposited = ["2015/6/16","2015/7/4","2015/7/6"]
    DateSampleRinsed = DateSampleDeposited
    concentration = 130 # ng/muL
    vol = 20 # uL loaded
    description = "Standard Circular DNA"
    MoleculeName = SQL_BOOT_CYPHER_DEF_SAMPLE_TYPE
    SamplePrep = SQL_BOOT_CYPHER_DEF_SAMPLE_PREP
    n = len(DateSampleCreated)
    for i in range(n):
        mSample = mCls.Sample(Name=description + str(i),
                              DateCreated = DateSampleCreated[i],
                              DateDeposited = DateSampleDeposited[i],
                              DateRinsed  = DateSampleRinsed[i],
                              VolLoadedMuL = vol,
                              ConcNanogMuL= concentration,
                              idMolType = MoleculeName,
                              idSamplePrep= SamplePrep,
                              Description = description)
        SqlDataModel.Insert(sess,mSample)

def AddDefaultModels(sess,mCls):
    mModels = HighBandwidthModel.HighBandwidthModel()
    # add a couple of models to use...
    SqlDataModel.Insert(sess,mCls.Model(Name=mModels.ModelName(),
                                        Description=""))

def AddDefaultExpertiments(sess,mCls):
    # add a couple of experiments to use...
    SqlDataModel.Insert(sess,mCls.ExpMeta(Name="Image",Description="",
                                          SourceFile="Image.pxp"))
    SqlDataModel.Insert(sess,mCls.ExpMeta(Name="Image1",Description="",
                                          SourceFile="Image1.pxp"))
    
    
def AddDefaultTipManifests(sess,mCls):
    TimeMade = [datetime.datetime(year=2015,month=6,day=16),
                datetime.datetime(year=2015,month=7,day=14)]
    TipProtocol  = [1,1]
    TipTypes = [SQL_BOOT_CYPHER_LONG,SQL_BOOT_CYPHER_FIBMINI]
    TipPack = [1,1]
    Name = ["BioLong6/16","BioMini7/14"]
    PackPosition = ["Unknown","Unknown"]
    for i in range(len(TimeMade)):
        timeMade = TimeMade[i]
        mTip = mCls.TipManifest(Name=Name[i],
                                Description="",
                                PackPosition=PackPosition[i],
                                TimeMade=timeMade,
                                TimeRinsed=timeMade,
                                idTipPrep=TipProtocol[i],
                                idTipPack=TipPack[i],
                                idTipType=TipTypes[i])
        SqlDataModel.Insert(sess,mTip)


                        
def run(Database="DebugCypher",
        PathToBootstrap=SqlUtil.SQL_BASE_LOCAL):
    """
    Nuke the database of choice (debug by default) and rebuild

    Args:
        Database: name of the database to nuke and rebuild. 

        PathToBootstrap: Path the whichever databasse we want 
    
    """
    ToBootstrap = PathToBootstrap  + Database
    mSqlObj = SqlUtil.InitSqlGetSessionAndClasses(databaseStr=ToBootstrap)
    mCls,sess = SqlDataModel.GetClassesAndSess(mSqlObj)
    tables = SqlDataModel.GetAllTables(mSqlObj)
    engine = mSqlObj._engine
    for tbl in reversed(tables):
        # delete and truncate (latter resets counter)
        engine.execute(tbl.delete())
        engine.execute("ALTER TABLE {:s} AUTO_INCREMENT = 1".format(tbl))
    #POST: every table is cleared
    args=(sess,mCls)
    AddDefaultTipPack(*args)
    AddDefaultTipTypes(*args)
    AddDefaultMolecules(*args)
    AddDefaultRatings(*args)
    AddDefaultUsers(*args)
    AddDefaultTipPreps(*args)
    AddDefaultSamplePreps(*args)
    AddDefaultTipManifests(*args)
    AddDefaultSamples(*args)
    AddDefaultModels(*args)
    AddDefaultExpertiments(*args)

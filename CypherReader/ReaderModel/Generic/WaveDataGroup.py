from CypherReader.IgorAdapter import ProcessSingleWave as ProcessSingleWave
import PyUtil.CypherUtil as CypherUtil

# Class for storing associated waves from a known data file
class WaveDataGroup():
    def __init__(self,AssociatedWaves):
        """
        Groups a single set of waves with a known file
        Args: 
             AssociatedWaves : The waves associated together (eg: Zsnsr, DeflV)
             as a dictionary. <Ending>:<WaveObj> as <Key>:<Pairs>

        Returns:
             None
        """
        self.AssociatedWaves =AssociatedWaves
        self.SqlIds = None
        self.HighBandwidthWaves = None
    def CreateTimeSepForceWaveObjectFromData(self,data):
        """
        Creates Separation and Force Wave Object from whatever input we are 
        given. Uses cypher naming conventions to determine what the waves are.

        Unit tested by "UnitTests/PythonReader/CypherConverter"

        Args: 
             Data: a dictionary of <ending>:<ProcessSingleWave.WaveObj> 
             key-value pairs
        Returns:
             A WaveObject, with three columns, for time, separation, and force
             corresponding
        """
        Sep,Force = CypherUtil.GetSepForce(data)
        Note = self.DataNote(data)
        # implicitly use the first wave as the 'meta' wave, to get the timing,
        # etc.
        Waves= [ProcessSingleWave.WaveObj(DataY=Sep,Note=Note),
                ProcessSingleWave.WaveObj(DataY=Force,Note=Note)]
        return ProcessSingleWave.ConcatenateWaves(Waves)
    def DataNote(self,data):
        """
        Gets the data note for a specific data set (dictionary of waves)

        Unit tested by "UnitTests/PythonReader/CypherConverter"

        Args: 
             Data: a dictionary of <ending>:<ProcessSingleWave.WaveObj> 
             key-value pairs
        Returns:
             Note corresponding to that element
        """
        key = sorted(data.keys())[0]
        return data[key].Note
    def Note(self):
        """
        Returns the note object for this data, assumed to be any of the 
        low-res associated waves 
        """
        return self.DataNote(self.AssociatedWaves)
    def CreateTimeSepForceWaveObject(self):
        """
        Creates Separation and Force Wave Object from whatever (low BW) 
        input we are given. Uses cypher naming conventions to determine what
        the waves are.

        Unit tested by "UnitTests/PythonReader/CypherConverter"

        Args: 
             None
        Returns:
             A WaveObject, with three columns, for time, separation, and force
        """
        # get the concatenated, low-bandwidth data.
        return self.CreateTimeSepForceWaveObjectFromData(self.AssociatedWaves)
    def SetSqlIds(self,idV):
        """
        Sets the Sql Ids for this object

        Args: 
             idV: return from PushToDatabase
        Returns:
             None
        """
        self.SqlIds = idV
    def __getitem__(self,index):
        """
        Gets the wave name with (String) ending index

        Args: 
             index: string ending
        Returns:
             WaveObj corresponding to the index
        """
        return self.AssociatedWaves[index]
    # below, we re-implement common methods so they act on the actual data.
    def keys(self):
        return self.AssociatedWaves.keys()
    def values(self):
        return self.AssociatedWaves.values()
    def __len__(self):
        return len(self.keys())
    """
    High-resolution functions below
    """
    def AssertHighBW(self):
        """
        Asserts that the wave has high-bandwidth data
        """
        assert self.HasHighBandwidth() , "No High Bandwidth data created"
    def HighBandwidthGetForce(self):
        """
        Given our high input waves, converts whatever Y we have into a 
        force and returns the associated WaveObject. Useful (for example)
        if we want to plot the high res force versus time (we don't yet have
        a high-resolution force

        Unit tested by "UnitTests/PythonReader/CypherConverter"

        Args: 
             None
        Returns:
             WaveObj corresponding to the index
        """
        self.AssertHighBW()
        # get the force for the wave
        force = CypherUtil.GetForce(self.HighBandwidthWaves)
        return force
    def HighBandwidthCreateTimeSepForceWaveObject(self):
        """
        Returns the high-bandwidth force and separation objects, assuming
        "HighBandwidthSetAssociatedWaves" has already been called

        Args: 
             None
        Returns:
             WaveObj corresponding to the index
        """
        self.AssertHighBW()
        # POST: have (something) to return.
        waves = self.HighBandwidthWaves
        return self.CreateTimeSepForceWaveObjectFromData(waves)
    def HasHighBandwidth(self):
        """
        Returns true if there is valid high-bandwidth data associated with the 
        model

        Unit tested by "UnitTests/PythonReader/CypherConverter"

        Args: 
             None
        Returns:
             WaveObj corresponding to the index
        """
        return self.HighBandwidthWaves is not None
    def HighBandwidthSetAssociatedWaves(self,AssocWaves):
        """
        Sets the (instance) high bandwidth data to "AssocWaves"

        Unit tested by "UnitTests/PythonReader/CypherConverter"

        Args: 
             AssocWaves: See init, AssociatedWaves argument.
        Returns:
             WaveObj corresponding to the index
        """
        self.HighBandwidthWaves = AssocWaves

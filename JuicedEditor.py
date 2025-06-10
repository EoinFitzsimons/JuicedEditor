import winreg

print()
print("Juiced Editor v2 dev")
print("    by N1GHTMAR3    ")
print("   June 10th 2025   ")
print()

class regKey:
    def __init__(self):
        regKeyObj = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, "Software\THQ\Juiced")
        # Supporting
        self.audioflags = winreg.QueryValueEx(regKeyObj, "audioflags")[0]
        self.audioflagsBin = bin(61 - self.audioflags)
        # Required
        self.displayAdapter = winreg.QueryValueEx(regKeyObj, "Adapter")[0] # Figure out how this value is determined
        self.resX = winreg.QueryValueEx(regKeyObj, "rezWidth")[0]
        self.resY = winreg.QueryValueEx(regKeyObj, "rezHeight")[0]
        self.resD = winreg.QueryValueEx(regKeyObj, "rezDepth")[0]
        self.antiAliasing = winreg.QueryValueEx(regKeyObj, "Antialiasing")[0]
        self.windowed = bool(winreg.QueryValueEx(regKeyObj, "Windowed")[0])
        self.widescreen = bool(winreg.QueryValueEx(regKeyObj, "widescreen")[0])
        self.multiThreading = bool(winreg.QueryValueEx(regKeyObj, "threading")[0])
        self.shaders = winreg.QueryValueEx(regKeyObj, "Shaders")[0]
        self.speech = bool(int(self.audioflagsBin[-5]))
        self.music = bool(int(self.audioflagsBin[-4]))
        self.hardwareMixing = bool(int(self.audioflagsBin[-2]))
        self.EAX = bool(int(self.audioflagsBin[-3]))
        self.allAudio = bool(int(self.audioflagsBin[-1]))
        self.multiTurnWheel = bool(winreg.QueryValueEx(regKeyObj, "MultiTurn")[0])
        # Optional
        try:
            self.apppath = winreg.QueryValueEx(regKeyObj, "apppath")[0]
        except FileNotFoundError:
            self.apppath = None
        try:
            self.language = winreg.QueryValueEx(regKeyObj, "Language")[0]
        except FileNotFoundError:
            self.language = 0
        
    
    # Read the currently set audio flags and set them up to put back in the registry.
    def encodeAudioFlags(self):
        afValue = 61
        if self.speech:
            afValue -= 16
        if self.music:
            afValue -= 8
        '''
        Doesn't work
        if self.EAX:
            afValue -= 4
        '''
        if self.hardwareMixing:
            afValue -= 2
        if self.allAudio:
            afValue -= 1
        return afValue

    # Read the int value for the language and determine which language it corresponds to.
    def decodeLanguage(self):
        '''
        Language is read as decimal; defaults to English if value out of range

        English = 9
        French  = 1036
        German  = 7
        Italian = 16
        Spanish = 10
        '''
        if self.language == 1036:
            return "French"
        elif self.language == 7:
            return "German"
        elif self.language == 16:
            return "Italian"
        elif self.language == 10:
            return "Spanish"
        else:
            return "English"
    
    # Print all registry values to the console.
    def displayValues(self):
        if self.apppath == None:
            print("Game directory: unknown")
        else:
            print("Game directory: " + self.apppath)
        print("Language: " + self.decodeLanguage())
        print("Display adapter: " + str(self.displayAdapter))
        print("Resolution: " + str(self.resX) + "x" + str(self.resY) + " (" + str(self.resD) + "-bit color depth)")
        print("Antialiasing level " + str(self.antiAliasing))
        print("Windowed: " + str(self.windowed))
        print("Widescreen: " + str(self.widescreen))
        print("Multithreading: " + str(self.multiThreading))
        if self.shaders == 0:
            print("No shaders")
        else:
            print ("Shader " + str(self.shaders) + ".0")
        print("Speech: " + str(self.speech))
        print("Music: " + str(self.music))
        print("Hardware mixing: " + str(self.hardwareMixing))
        print("EAX: " + str(self.EAX))
        print("All audio: " + str(self.allAudio))

try:
    reg = regKey()
    reg.displayValues()
except FileNotFoundError:
    print("No registry key found. Please run JuicedConfig.exe.")
from os import getcwd
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide2.QtCore import QFile, QIODevice, Qt
from PySide2.QtUiTools import QUiLoader
import struct
import sys
import winreg

checkForUpdates = True
autoDetectInstall = True
advanced = False

print()
print("                 Juiced Editor v2 dev                 ")
print("                     by N1GHTMAR3                     ")
print("                    June 13th 2025                    ")
print("https://github.com/N1GHT-MAR3/JuicedEditor/tree/rewrite")
print()

class binary:
    def __init__(self, path):
        self.filePath = path
        self.binaryData = bytearray(open(path, "rb").read())

        self.platform = self.detectPlatform() # PC (.exe), Xbox (.xbe), or PS2 (elf)
        self.version = self.detectVersion()
        self.isJapanese = self.platform == 2 and self.version == 4
        self.decrypted = self.checkEncryption()
        self.serversPatched = self.checkServers() # PC exclusive
        self.saveFolder = self.getSaveFolderName() # PC exclusive
        self.carmodelsPatched = b"dummyfile.dat" in self.binaryData # PC exclusive
        self.disablePinkSlipCalls = None # Decrypted only
        self.cheatOffset = self.binaryData.find(b"\x96\x00\x00\x00\xC8\x00\x00\x00\xC8\x00\x00\x00") + 12
        self.cheatPINT = cheat(0, self.decodeCheatCode(0, self.isJapanese))
        self.cheatDOSH = cheat(1, self.decodeCheatCode(1, self.isJapanese), self.getDOSHValue())
        self.cheatRESP = cheat(2, self.decodeCheatCode(2, self.isJapanese), self.getRESPValue())
        self.cheatCARS = cheat(3, self.decodeCheatCode(3, self.isJapanese))
        self.cheatCREW = cheat(4, self.decodeCheatCode(4, self.isJapanese))
        self.cheatCHAR = cheat(5, self.decodeCheatCode(5, self.isJapanese))
        self.cheatWIN = cheat(6, self.decodeCheatCode(6, self.isJapanese))
        self.cheatALL = cheat(7, self.decodeCheatCode(7, self.isJapanese))
        # Japanese PS2 exclusive
        if self.isJapanese:
            self.cheatQADM = cheat(8, self.decodeCheatCode(8, True))
        self.carUnlocks = carUnlocks(self.getCarUnlockData())
    
    def diagnostic(self):
        print("Binary located at " + self.filePath)
        if self.platform == 0:
            print("Platform: PC")
            if self.version == 0:
                print("Version: retail .exe, unpatched")
            elif self.version == 1:
                print("Version: retail .exe, patched")
            elif self.version == 2:
                print("Version: hlm-juic cracked .exe")
            elif self.version == 3:
                print("Version: hlm-juif cracked .exe")
            elif self.version == 4:
                print("Version: Z3r0n3 v1 cracked .exe")
            elif self.version == 5:
                print("Version: Z3r0n3 v2 cracked .exe")
            if self.serversPatched:
                print("OpenSpy servers patched in")
            else:
                print("OpenSpy servers not patched in")
        elif self.platform == 1:
            print("Platform: Xbox")
            if self.version == 0:
                print("Version: original")
            elif self.version == 1:
                print("Version: TU1")
        elif self.platform == 2:
            print("Platform: PlayStation 2")
            if self.version == 0:
                print("North American version (SLUS-20872)")
            elif self.version == 1:
                print("Korean version (SLKA-25283)")
            elif self.version == 2:
                print("European version (SLES-53044)")
            elif self.version == 3:
                print("Italian version (SLES-53151)")
            elif self.version == 4:
                print("Japanese version (SLPM-66277)")
        print("Decrypted: " + str(self.decrypted))
        if self.platform == 0:
            print(self.saveFolder)
        if self.carmodelsPatched:
            print("dummyfile.dat")
        else:
            if self.platform == 0:
                print("carmodels.dat")
        print("Cheat code offset: " + str(self.cheatOffset))
        print("PINT code: " + self.cheatPINT.code + " " + str(self.cheatPINT.enabled))
        if self.platform == 2 and self.version == 4:
            print("QADM code: " + self.cheatQADM.code + " " + str(self.cheatQADM.enabled))
        print("DOSH code: " + self.cheatDOSH.code + " " + str(self.cheatDOSH.enabled))
        print("RESP code: " + self.cheatRESP.code + " " + str(self.cheatRESP.enabled))
        print("CARS code: " + self.cheatCARS.code + " " + str(self.cheatCARS.enabled))
        print("CREW code: " + self.cheatCREW.code + " " + str(self.cheatCREW.enabled))
        print("CHAR code: " + self.cheatCHAR.code + " " + str(self.cheatCHAR.enabled))
        print("WIN code: " + self.cheatWIN.code + " " + str(self.cheatWIN.enabled))
        print("ALL code: " + self.cheatALL.code + " " + str(self.cheatALL.enabled))
        print()
    
    def detectPlatform(self):
        # PC
        if self.binaryData[0:2] == b"MZ":
            return 0
        # Xbox
        elif self.binaryData[0:3] == b"XBE":
            return 1
        # PS2
        elif self.binaryData[1:4] == b"ELF":
            return 2
        else:
            return None
    
    def detectVersion(self):
        # PC
        if self.platform == 0:
            if len(self.binaryData) == 12533760:
                # Legitimate unpatched version
                if self.binaryData[3512:3515] == b"\x20\x63\x9f":
                    return 0
                # hlm-juic
                elif self.binaryData[3512:3515] == b"\x56\xaf\x1c":
                    return 2
            # Legitimate patched version
            elif len(self.binaryData) == 6852608:
                return 1
            # hlm-juif
            elif len(self.binaryData) == 12560384:
                return 3
            # Z3r0n3 v1
            elif len(self.binaryData) == 30097408:
                return 4
            # Z3r0n3 v2
            elif len(self.binaryData) == 13760830:
                return 5
            # Unknown
            else:
                return None
        # Xbox
        elif self.platform == 1:
            # unpatched
            if self.binaryData[4] == 255:
                return 0
            # patched
            elif self.binaryData[4] == 247:
                return 1
            # unknown
            else:
                return None
        # PS2
        elif self.platform == 2:
            offset = self.binaryData.find(b"JUICED Driver") + 24
            serial = self.binaryData[offset : offset + 10]
            # North America
            if serial == b"SLUS-20872":
                return 0
            # South Korea
            elif serial == b"SLKA-25283":
                return 1
            # Europe (except Italy)
            elif serial == b"SLES-53044":
                return 2
            # Italy
            elif serial == b"SLES-53151":
                return 3
            # Japan
            elif serial == b"SLPM-66277":
                return 4
            # Unknown
            else:
                return None
        # Unknown
        else:
            return None
    
    def getVersionString(self):
        version = ""
        if self.platform == 0:
            version += "PC ("
            if self.version == 0:
                version += "retail, unpatched)"
            elif self.version == 1:
                version += "retail, patched)"
            elif self.version == 2:
                version += "hlm-juic, unpatched)"
            elif self.version == 3:
                version += "hlm-juif, unpatched)"
            elif self.version == 4:
                version += "Z3r0n3 v1, patched)"
            elif self.version == 5:
                version += "Z3r0n3 v2, patched)"
            else:
                version += "unknown)"
        elif self.platform == 1:
            version += "Xbox ("
            if self.version == 0:
                version += "unpatched)"
            elif self.version == 1:
                version += "patched)"
            else:
                version += "unknown)"
        elif self.platform == 2:
            version += "PlayStation 2 ("
            if self.version == 0:
                version += "SLUS-20872)"
            elif self.version == 1:
                version += "SLKA-25283)"
            elif self.version == 2:
                version += "SLES-53044)"
            elif self.version == 3:
                version += "SLES-53151)"
            elif self.version == 4:
                version += "SLPM-66277)"
            else:
                version += "unknown)"
        else:
            version = "Unknown"
        return version
    
    def checkEncryption(self):
        if self.platform == 2:
            return False
        else:
            if self.platform == 0 and self.version < 2:
                return False
            else:
                return True
    
    def checkServers(self):
        if self.platform == 0:
            if self.binaryData.count(b"openspy.com") < 9:
                return False
            else:
                return True
        else:
            return False
    
    def getSaveFolderName(self):
        if self.platform == 0:
            offset = self.binaryData.find(b"\x53\x00\x00\x00\x00\x80\x46") + 7
            return self.binaryData[offset : offset + 4].decode()
        else:
            return None
    
    def decodeCheatCode(self, id, japanese):
        code = ""
        if not japanese or id == 0:
            codeBytes = self.binaryData[self.cheatOffset + (id * 4) : self.cheatOffset + ((id + 1) * 4)]
        else:
            if id == 8:
                codeBytes = self.binaryData[self.cheatOffset + 4 : self.cheatOffset + 8]
            elif id > 0 and id < 8:
                codeBytes = self.binaryData[self.cheatOffset + ((id + 1) * 4) : self.cheatOffset + ((id + 2) * 4)]
        for i in codeBytes:
            if i == 136:
                code += "."
            else:
                code += chr(i - 90)
        return code
    
    def getDOSHValue(self):
        if self.decrypted:
            if self.platform == 0:
                offset = self.binaryData.find(b"\x2C\xC2\x04\x00\xC7\x47\x0C") + 7
            elif self.platform == 1:
                offset = self.binaryData.find(b"\x04\x00\xC7\x47\x0C") + 5
            return int.from_bytes(self.binaryData[offset : offset + 4], "little")
        else:
            return None
    
    def getRESPValue(self):
        if self.decrypted:
            if self.platform == 0:
                offset = self.binaryData.find(b"\x01\x00\x8B\x13\x68") + 5
                return int(struct.unpack("f", self.binaryData[offset : offset + 4])[0])
            elif self.platform == 1:
                offset = self.binaryData.find(b"\x13\xC7\x42\x70") + 4
                return int.from_bytes(self.binaryData[offset : offset + 4], "little")
        else:
            return None
    
    def getCarUnlockData(self):
        if self.platform == 0:
            if self.version == 1 or self.version == 4 or self.version == 5:
                offset = self.binaryData.find(b"\x80\x6C\x6F\x00\x00\x00\x00\x00\x00\x00\x00\x00") + 12
            elif self.version == 0 or self.version == 2 or self.version == 3:
                offset = self.binaryData.find(b"\x48\x3C\x6F\x00\x00\x00\x00\x00\x00\x00\x00\x00") + 12
        elif self.platform == 1:
            if self.version == 0:
                offset = self.binaryData.find(b"\x48\xF2\x2F\x00\x00\x00\x00\x00\x00\x00\x00\x00") + 12
            elif self.version == 1:
                offset = self.binaryData.find(b"\x10\xFE\x2F\x00\x00\x00\x00\x00\x00\x00\x00\x00") + 12
        elif self.platform == 2:
            offset = self.binaryData.find(b"\x41\x00\x00\x00\x40\x00\x00\x00\x00") + 9
        return self.binaryData[offset : offset + 208]


class cheat:
    def __init__(self, id, code, value = None):
        self.id = id
        self.code = code
        self.enabled = code[0] != "1"
        self.value = value


class carUnlocks:
    carIDs = ("celica", "civicr", "clio", "crx", "focus", "evo8", "gtr", "imp", "nsx", "peugeot_206", "rx7", "trans", "vette_zo6", "viper", "vw_corrado", "punto", "golf", "corsa", "eclipse", "s2000", "supra", "integra", "mx5", "civic_97", "mustang68", "neon", "monaro", "wrx2", "fto", "celica_2", "mr2", "evo6", "prelude", "300zx", "350z", "3000gt", "integra2", "mustang2", "camaro", "charger", "corolla", "dodge_srt", "vette_2", "mrs", "camaro70", "falcon", "rsx", "ac_integra", "ac_nsx", "rx8", "beetle", "focus_2")

    def __init__(self, data):
        self.callThisSomethingElse = {}
        for i in range(52):
            self.callThisSomethingElse[self.carIDs[i]] = int.from_bytes(data[i * 4 : (i + 1) * 4], "little")


class regKey:
    def __init__(self):
        regKeyObj = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, "Software\\THQ\\Juiced")
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
    def diagnostic(self):
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


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class ui:
    def __init__(self, path):
        self.uiFile = QFile(path)
        loader = QUiLoader()
        self.window = loader.load(self.uiFile)
        self.uiFile.close()
    
        self.window.actionOpen.triggered.connect(self.openBinary)
        self.window.modsServerButton.clicked.connect(self.patchServers)
        self.window.cheatsPINTCheckbox.stateChanged.connect(self.togglePINT)
        self.window.cheatsDOSHCheckbox.stateChanged.connect(self.toggleDOSH)
        self.window.cheatsRESPCheckbox.stateChanged.connect(self.toggleRESP)
        self.window.cheatsCARSCheckbox.stateChanged.connect(self.toggleCARS)
        self.window.cheatsCREWCheckbox.stateChanged.connect(self.toggleCREW)
        self.window.cheatsCHARCheckbox.stateChanged.connect(self.toggleCHAR)
        self.window.cheatsWINCheckbox.stateChanged.connect(self.toggleWIN)
        self.window.cheatsALLCheckbox.stateChanged.connect(self.toggleALL)
        self.window.cheatsQADMCheckbox.stateChanged.connect(self.toggleQADM)
    
    def openBinary(self):
        self.loadedBinary = binary(QFileDialog.getOpenFileName(self.window, "Open...", getcwd(), "All supported files (*.exe *.xbe SLUS_208.72 SLKA_252.83 SLES_530.44 SLES_531.51 SLPM_662.77)")[0])
        self.loadedBinary.diagnostic()
        if self.loadedBinary.platform == 0:
            try:
                self.loadedReg = regKey()
                self.loadedReg.diagnostic()
            except FileNotFoundError:
                print("No registry key found. Please run JuicedConfig.exe.")
                QMessageBox.critical(self.window, "Error", "No registry key found. Please run JuicedConfig.exe to access Registry values.")
        self.initializeUI()
    
    def initializeUI(self):
        # Info section
        self.window.binaryFilePath.setText(self.loadedBinary.filePath[:self.loadedBinary.filePath.rfind("/")])
        self.window.binaryFileName.setText(self.loadedBinary.filePath[self.loadedBinary.filePath.rfind("/") + 1:] + " (" + str(len(self.loadedBinary.binaryData)) + " bytes)")
        self.window.binaryVersionDesc.setText(self.loadedBinary.getVersionString())
        if self.loadedBinary.decrypted:
            self.window.binaryDecryptedDesc.setStyleSheet("color: blue")
            self.window.binaryDecryptedDesc.setText("Yes")
        else:
            self.window.binaryDecryptedDesc.setStyleSheet("color: red")
            self.window.binaryDecryptedDesc.setText("No")
        # Modifications section
        if self.loadedBinary.platform == 0:
            if self.loadedBinary.serversPatched:
                self.window.modsServerStatus.setStyleSheet("color: blue")
                self.window.modsServerStatus.setText("Patched")
                self.window.modsServerButton.setEnabled(False)
            else:
                self.window.modsServerStatus.setStyleSheet("color: red")
                self.window.modsServerStatus.setText("Unpatched")
                self.window.modsServerButton.setEnabled(True)
        else:
            self.window.modsServerStatus.setStyleSheet("color: black")
            self.window.modsServerStatus.setText("N/A")
            self.window.modsServerButton.setEnabled(False)
        if self.loadedBinary.platform == 0:
            self.window.modsSaveFolder.setText(self.loadedBinary.saveFolder)
            self.window.modsSaveFolder.setEnabled(True)
        else:
            self.window.modsSaveFolder.setEnabled(False)
        self.window.modsCarUnlocks.setEnabled(True)
        # Cheats section
        self.window.cheatsPINTCheckbox.setEnabled(True)
        if self.loadedBinary.cheatPINT.enabled:
            self.window.cheatsPINTCheckbox.setChecked(True)
            self.window.cheatsPINTCode.setText(self.loadedBinary.cheatPINT.code)
            self.window.cheatsPINTCode.setEnabled(True)
        else:
            self.window.cheatsPINTCheckbox.setChecked(False)
            self.window.cheatsPINTCode.setEnabled(False)
        self.window.cheatsDOSHCheckbox.setEnabled(True)
        if self.loadedBinary.cheatDOSH.enabled:
            self.window.cheatsDOSHCheckbox.setChecked(True)
            self.window.cheatsDOSHCode.setText(self.loadedBinary.cheatDOSH.code)
            self.window.cheatsDOSHCode.setEnabled(True)
            if self.loadedBinary.decrypted:
                self.window.cheatsDOSHValue.setValue(self.loadedBinary.cheatDOSH.value)
                self.window.cheatsDOSHValue.setEnabled(True)
        else:
            self.window.cheatsDOSHCheckbox.setChecked(False)
            self.window.cheatsDOSHCode.setEnabled(False)
            self.window.cheatsDOSHValue.setEnabled(False)
        self.window.cheatsRESPCheckbox.setEnabled(True)
        if self.loadedBinary.cheatRESP.enabled:
            self.window.cheatsRESPCheckbox.setChecked(True)
            self.window.cheatsRESPCode.setText(self.loadedBinary.cheatRESP.code)
            self.window.cheatsRESPCode.setEnabled(True)
            if self.loadedBinary.decrypted:
                self.window.cheatsRESPValue.setValue(self.loadedBinary.cheatRESP.value)
                self.window.cheatsRESPValue.setEnabled(True)
        else:
            self.window.cheatsRESPCheckbox.setChecked(False)
            self.window.cheatsRESPCode.setEnabled(False)
            self.window.cheatsRESPValue.setEnabled(False)
        self.window.cheatsCARSCheckbox.setEnabled(True)
        if self.loadedBinary.cheatCARS.enabled:
            self.window.cheatsCARSCheckbox.setChecked(True)
            self.window.cheatsCARSCode.setText(self.loadedBinary.cheatCARS.code)
            self.window.cheatsCARSCode.setEnabled(True)
        else:
            self.window.cheatsCARSCheckbox.setChecked(False)
            self.window.cheatsCARSCode.setEnabled(False)
        self.window.cheatsCREWCheckbox.setEnabled(True)
        if self.loadedBinary.cheatCREW.enabled:
            self.window.cheatsCREWCheckbox.setChecked(True)
            self.window.cheatsCREWCode.setText(self.loadedBinary.cheatCREW.code)
            self.window.cheatsCREWCode.setEnabled(True)
        else:
            self.window.cheatsCREWCheckbox.setChecked(False)
            self.window.cheatsCREWCode.setEnabled(False)
        self.window.cheatsCHARCheckbox.setEnabled(True)
        if self.loadedBinary.cheatCHAR.enabled:
            self.window.cheatsCHARCheckbox.setChecked(True)
            self.window.cheatsCHARCode.setText(self.loadedBinary.cheatCHAR.code)
            self.window.cheatsCHARCode.setEnabled(True)
        else:
            self.window.cheatsCHARCheckbox.setChecked(False)
            self.window.cheatsCHARCode.setEnabled(False)
        self.window.cheatsWINCheckbox.setEnabled(True)
        if self.loadedBinary.cheatWIN.enabled:
            self.window.cheatsWINCheckbox.setChecked(True)
            self.window.cheatsWINCode.setText(self.loadedBinary.cheatWIN.code)
            self.window.cheatsWINCode.setEnabled(True)
        else:
            self.window.cheatsWINCheckbox.setChecked(False)
            self.window.cheatsWINCode.setEnabled(False)
        self.window.cheatsALLCheckbox.setEnabled(True)
        if self.loadedBinary.cheatALL.enabled:
            self.window.cheatsALLCheckbox.setChecked(True)
            self.window.cheatsALLCode.setText(self.loadedBinary.cheatALL.code)
            self.window.cheatsALLCode.setEnabled(True)
        else:
            self.window.cheatsALLCheckbox.setChecked(False)
            self.window.cheatsALLCode.setEnabled(False)
        if self.loadedBinary.platform == 2 and self.loadedBinary.version == 4:
            self.window.cheatsQADMCheckbox.setEnabled(True)
            if self.loadedBinary.cheatQADM.enabled:
                self.window.cheatsQADMCheckbox.setChecked(True)
                self.window.cheatsQADMCode.setText(self.loadedBinary.cheatQADM.code)
                self.window.cheatsQADMCode.setEnabled(True)
            else:
                self.window.cheatsQADMCheckbox.setChecked(False)
                self.window.cheatsQADMCode.setEnabled(False)
        else:
            self.window.cheatsQADMCheckbox.setEnabled(False)
            self.window.cheatsQADMCheckbox.setChecked(False)
            self.window.cheatsQADMCode.setEnabled(False)
        # Registry section
        if self.loadedBinary.platform == 0 and self.loadedReg:
            self.window.regResW.setValue(self.loadedReg.resX)
            self.window.regResW.setEnabled(True)
            self.window.regResH.setValue(self.loadedReg.resY)
            self.window.regResH.setEnabled(True)
            if self.loadedReg.resD == 32:
                self.window.regDepth.setChecked(True)
            else:
                self.window.regDepth.setChecked(False)
            self.window.regDepth.setEnabled(True)
            self.window.regWindowed.setChecked(self.loadedReg.windowed)
            self.window.regWindowed.setEnabled(True)
            self.window.regWidescreen.setChecked(self.loadedReg.widescreen)
            self.window.regWidescreen.setEnabled(True)
            self.window.regAALevel.setCurrentIndex(self.loadedReg.antiAliasing)
            self.window.regAALevel.setEnabled(True)
            self.window.regShaderLevel.setCurrentIndex(self.loadedReg.shaders)
            self.window.regShaderLevel.setEnabled(True)
            self.window.regMultithreading.setChecked(self.loadedReg.multiThreading)
            self.window.regMultithreading.setEnabled(True)
            self.window.regAudioAll.setChecked(self.loadedReg.allAudio)
            self.window.regAudioAll.setEnabled(True)
            self.window.regAudioHW.setChecked(self.loadedReg.hardwareMixing)
            self.window.regAudioHW.setEnabled(True)
            self.window.regAudioMusic.setChecked(self.loadedReg.music)
            self.window.regAudioMusic.setEnabled(True)
            self.window.regAudioSpeech.setChecked(self.loadedReg.speech)
            self.window.regAudioSpeech.setEnabled(True)
            self.window.regMultiTurnWheel.setChecked(self.loadedReg.multiTurnWheel)
            self.window.regMultiTurnWheel.setEnabled(True)
        else:
            self.window.regResW.setEnabled(False)
            self.window.regResH.setEnabled(False)
            self.window.regDepth.setEnabled(False)
            self.window.regWindowed.setEnabled(False)
            self.window.regWidescreen.setEnabled(False)
            self.window.regAALevel.setEnabled(False)
            self.window.regShaderLevel.setEnabled(False)
            self.window.regMultithreading.setEnabled(False)
            self.window.regAudioAll.setEnabled(False)
            self.window.regAudioHW.setEnabled(False)
            self.window.regAudioMusic.setEnabled(False)
            self.window.regAudioSpeech.setEnabled(False)
            self.window.regMultiTurnWheel.setEnabled(False)
        # Experimental section
        if self.loadedBinary.platform == 0:
            if self.loadedBinary.carmodelsPatched:
                self.window.expCarmodels.setChecked(True)
            else:
                self.window.expCarmodels.setChecked(False)
            self.window.expCarmodels.setEnabled(True)
        else:
            self.window.expCarmodels.setEnabled(False)
        

    def patchServers(self):
        while b"gamespy.com" in self.loadedBinary.binaryData:
            self.loadedBinary.binaryData[self.loadedBinary.binaryData.index(b"gamespy.com") : self.loadedBinary.binaryData.index(b"gamespy.com") + 11] = b"openspy.net"
        self.window.modsServerStatus.setStyleSheet("color: blue")
        self.window.modsServerStatus.setText("Patched")
        self.window.modsServerButton.setEnabled(False)
    

    def togglePINT(self):
        if self.window.cheatsPINTCheckbox.isChecked():
            self.window.cheatsPINTCode.setEnabled(True)
        else:
            self.window.cheatsPINTCode.setEnabled(False)
    
    def toggleDOSH(self):
        if self.window.cheatsDOSHCheckbox.isChecked():
            self.window.cheatsDOSHCode.setEnabled(True)
            if self.loadedBinary.decrypted:
                self.window.cheatsDOSHValue.setEnabled(True)
        else:
            self.window.cheatsDOSHCode.setEnabled(False)
            self.window.cheatsDOSHValue.setEnabled(False)
    
    def toggleRESP(self):
        if self.window.cheatsRESPCheckbox.isChecked():
            self.window.cheatsRESPCode.setEnabled(True)
            if self.loadedBinary.decrypted:
                self.window.cheatsRESPValue.setEnabled(True)
        else:
            self.window.cheatsRESPCode.setEnabled(False)
            self.window.cheatsRESPValue.setEnabled(False)

    def toggleCARS(self):
        if self.window.cheatsCARSCheckbox.isChecked():
            self.window.cheatsCARSCode.setEnabled(True)
        else:
            self.window.cheatsCARSCode.setEnabled(False)
    
    def toggleCREW(self):
        if self.window.cheatsCREWCheckbox.isChecked():
            self.window.cheatsCREWCode.setEnabled(True)
        else:
            self.window.cheatsCREWCode.setEnabled(False)
    
    def toggleCHAR(self):
        if self.window.cheatsCHARCheckbox.isChecked():
            self.window.cheatsCHARCode.setEnabled(True)
        else:
            self.window.cheatsCHARCode.setEnabled(False)
    
    def toggleWIN(self):
        if self.window.cheatsWINCheckbox.isChecked():
            self.window.cheatsWINCode.setEnabled(True)
        else:
            self.window.cheatsWINCode.setEnabled(False)

    def toggleALL(self):
        if self.window.cheatsALLCheckbox.isChecked():
            self.window.cheatsALLCode.setEnabled(True)
        else:
            self.window.cheatsALLCode.setEnabled(False)
    
    def toggleQADM(self):
        if self.window.cheatsQADMCheckbox.isChecked():
            self.window.cheatsQADMCode.setEnabled(True)
        else:
            self.window.cheatsQADMCode.setEnabled(False)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    uiMain = ui("UI//main.ui")
    uiMain.window.show()
    sys.exit(app.exec_())
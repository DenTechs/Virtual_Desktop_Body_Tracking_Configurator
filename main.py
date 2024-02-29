from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QCheckBox, QGridLayout, QComboBox, QDoubleSpinBox, QTabWidget, QSpacerItem, QSizePolicy, QMessageBox
import json
from iobt_options import default_enabled, default_rotations, default_toggles, default_misc
import psutil
import winreg



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Virtual Desktop Body Tracking Configurator")
        
        for proc in psutil.process_iter(['name']):
            if "vrserver.exe" in proc.info['name'].lower():
                dlg2 = QMessageBox()
                dlg2.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
                dlg2.setText("Error!\nvrserver.exe running!\nPlease close SteamVR and try again")
                
                dlg2.exec()
                
                if QMessageBox.StandardButton.Ok:
                    exit()
        
        self.steam = ""
        try:
            location = winreg.HKEY_LOCAL_MACHINE
            path = winreg.OpenKeyEx(location, r"SOFTWARE\Wow6432Node\Valve\Steam")
            self.steam = winreg.QueryValueEx(path, "InstallPath")[0]
            self.steam = self.steam.replace("\\","/")
            if path:
                winreg.CloseKey(path)
        except Exception as e:
            dlg2 = QMessageBox()
            dlg2.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
            dlg2.setText(f"Error: {e}")
            
            dlg2.exec()
            
            if QMessageBox.StandardButton.Ok:
                exit()
        
        
        self.checkboxes = {}
        self.offsets = {}   
        self.misc = {}
        
        
        layoutTab1 = QGridLayout()
        self.layoutTab2 = QGridLayout()
        layoutTab3 = QVBoxLayout()


        for variable in default_toggles:
            button = QCheckBox(variable.replace("_", " ").title())
            button.setCheckable(True)
            button.setChecked(default_toggles.get(variable))
            
            self.misc[variable] = button
            
            layoutTab3.addWidget(button)
            
        for variable in default_misc:
            box = QDoubleSpinBox()
            box.setPrefix(f"{variable.replace('_', ' ').title()}: ")
            box.setMinimum(0)
            box.setMaximum(1)
            box.setSingleStep(0.05)
            box.setDecimals(3)
            box.setValue(default_misc[variable])
            
            self.misc[variable] = box
            
            layoutTab3.addWidget(box)      


        
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        spacer2 = QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        spacer3 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        layoutTab1.addItem(spacer, 16, 0)
        layoutTab1.addItem(spacer3,1,0)
        self.layoutTab2.addItem(spacer2,0, 1)
        
        self.upperWithHip = QPushButton("Upper Body (With Hip)")
        self.upperWithHip.clicked.connect(self.Upper_With_Hip_clicked)
        layoutTab1.addWidget(self.upperWithHip, 0, 0)
        
        self.upper = QPushButton("Upper Body Only")
        self.upper.clicked.connect(self.upper_only_clicked)
        layoutTab1.addWidget(self.upper, 0, 1)
        
        self.elbows = QPushButton("Elbows Only")
        self.elbows.clicked.connect(self.elbows_only_clicked)
        layoutTab1.addWidget(self.elbows, 0, 2)
        
        self.defaults = QPushButton("Reset Enabled Trackers to Defaults")
        self.defaults.clicked.connect(self.reset_clicked)
        layoutTab1.addWidget(self.defaults, 17, 0)
        
        self.export = QPushButton("Export Settings (All Pages)")
        self.export.clicked.connect(self.export_clicked)
        layoutTab1.addWidget(self.export, 17, 2)
        
        self.export2 = QPushButton("Export Settings (All Pages)")
        self.export2.clicked.connect(self.export_clicked)
        self.layoutTab2.addWidget(self.export2, 4, 0)
        
        self.export3 = QPushButton("Export Settings (All Pages)")
        self.export3.clicked.connect(self.export_clicked)
        layoutTab3.addWidget(self.export3, 10)
        
        first = 0
        row = 3
        column = 0
        for variable in default_enabled:
            button = QCheckBox(variable[:-8].replace("_", " ").title())
            button.setCheckable(True)
            button.setChecked(default_enabled.get(variable))
            button.clicked.connect(lambda checked, b=button: self.checkbox_interacted(b))
            
            self.checkboxes[variable] = button
            
            layoutTab1.addWidget(button, row, column)
            row += 1
            first += 1
            
            if row >= 16 or first == 7:
                row = 3
                column += 1
                
        widgetTab1 = QWidget()
        widgetTab1.setLayout(layoutTab1)
            
            
        self.dropdown = QComboBox()
            
        row = 0
        column = 0
        for variable in default_enabled: 

            self.dropdown.addItem(variable[:-8].replace("_", " ").title())
            
            self.offsets[variable] = {}
            
            for axis in ["Translate X", "Translate Y", "Translate Z", "Rotate X", "Rotate Y", "Rotate Z"]:
                box = QDoubleSpinBox()
                box.setPrefix(f"{axis}: ")
                
                if axis[:-2] == "Rotate":
                    box.setMaximum(360)
                    box.setMinimum(-360)
                    box.setSingleStep(90)
                    try:
                        box.setValue(default_rotations[f"{variable[:-8]}_rot_{axis[-1].lower()}"])
                    except:
                        ()
                else:
                    box.setSingleStep(0.1)
                    box.setDecimals(3)                    
                
                
                self.offsets[variable][axis] = box
                
                #layoutTab2.addWidget(box, row, column)

                row += 1
                
                if row >= 9:
                    row = 0
                    column += 1
        



        self.layoutTab2.addWidget(self.dropdown, 3, 0)
        i=1
        for axis in ["Translate X", "Translate Y", "Translate Z", "Rotate X", "Rotate Y", "Rotate Z"]:
            self.layoutTab2.addWidget(self.offsets[list(default_enabled.keys())[0]][axis],i,2   )
            i+=1
        self.dropdown.currentIndexChanged.connect(self.offset_index_changed)

        widgetTab2 = QWidget()
        widgetTab2.setLayout(self.layoutTab2)
        
        widgetTab3 = QWidget()
        widgetTab3.setLayout(layoutTab3)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(True)

        tabs.addTab(widgetTab1, "Enabled Trackers")
        tabs.addTab(widgetTab2, "Tracker Offsets")
        tabs.addTab(widgetTab3, "Miscellaneous")

        self.setCentralWidget(tabs)
        
        
        
    def offset_index_changed(self, index):
        i=1
        for axis in ["Translate X", "Translate Y", "Translate Z", "Rotate X", "Rotate Y", "Rotate Z"]:
            self.layoutTab2.addWidget(self.offsets[list(default_enabled.keys())[index]][axis],i,2)
            i+=1
        
        
        #print(index)
    
        
    def checkbox_interacted(self, checkbox):
        ()
        #print(f"{checkbox.text()} is {checkbox.isChecked()}")
     
    def reset_clicked(self):
        #print("Reset Defaults clicked")
        for variable, checkbox in self.checkboxes.items():
            default_state = default_enabled.get(variable, False)
            checkbox.setChecked(default_state)
        
    def Upper_With_Hip_clicked(self):
        #print("Upper With Hip clicked")
        for variable, checkbox in self.checkboxes.items():
            if variable == "left_arm_upper_joint_enabled" or variable == "left_arm_lower_joint_enabled" or variable == "right_arm_upper_joint_enabled" or variable == "right_arm_lower_joint_enabled" or variable == "chest_joint_enabled" or variable == "hips_joint_enabled":
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False) 

    def upper_only_clicked(self):
        #print("Upper Only clicked")
        for variable, checkbox in self.checkboxes.items():
            if variable == "left_arm_upper_joint_enabled" or variable == "left_arm_lower_joint_enabled" or variable == "right_arm_upper_joint_enabled" or variable == "right_arm_lower_joint_enabled" or variable == "chest_joint_enabled":
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
        
    def elbows_only_clicked(self):
        #print("Elbows Only clicked")
        for variable, checkbox in self.checkboxes.items():
            if variable == "left_arm_upper_joint_enabled" or variable == "left_arm_lower_joint_enabled" or variable == "right_arm_upper_joint_enabled" or variable == "right_arm_lower_joint_enabled":
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False) 
        
    def export_clicked(self):
        #print("Export clicked")
        export_dict = {}
        
        for variable, checkbox in self.checkboxes.items():
           if default_enabled[variable] != checkbox.isChecked():
                export_dict[variable] = checkbox.isChecked()
           
        for variable, joint in self.offsets.items():
            for axis, box in joint.items():
                if axis[:-2] == "Rotate":
                    try:
                        if abs(box.value() - default_rotations[f"{variable[:-8]}_rot_{axis[-1].lower()}"]) < 0.001:
                            break
                        else:
                            export_dict[f"{variable[:-8]}_rot_{axis[-1].lower()}"] = box.value()
                    except:
                        if box.value() >= 0.001:
                            export_dict[f"{variable[:-8]}_rot_{axis[-1].lower()}"] = box.value()
                else:
                    try:
                        if abs(box.value() - default_rotations[f"{variable[:-8]}_offset_{axis[-1].lower()}"]) < 0.001:
                            break
                        else:
                            export_dict[f"{variable[:-8]}_offset_{axis[-1].lower()}"] = box.value()
                    except:
                        if box.value() >= 0.001:
                            export_dict[f"{variable[:-8]}_offset_{axis[-1].lower()}"] = box.value()
                    
        for variable, input in self.misc.items():
            try:
                if abs(default_misc[variable] - input.value()) >= 0.001:
                    export_dict[variable] = input.value()
            except:
                ()
            try:
                if default_toggles[variable] != input.isChecked():
                    export_dict[variable] = input.isChecked()
            except:
                ()
            
           
        # with open("output.json", "w") as outfile:
        #     json.dump(export_dict, indent=2, fp=outfile)
                
        try:   
            with open(f"{self.steam}/config/steamvr.vrsettings", "r+") as settings:
                
                temp = json.load(settings)
                try:
                    with open(f"{self.steam}/config/steamvr.vrsettings.backup", "x") as backup:
                        json.dump(temp, fp=backup)
                        backup.close()
                except:
                    ()
                
                temp["driver_VirtualDesktop"] = export_dict
                #print(temp)
                settings.seek(0)
                json.dump(temp, indent=3, fp=settings)
                settings.truncate()
                settings.close()
                
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
                dlg.setText(f"Successfully exported to SteamVR!\nBackup of original is saved at: {self.steam}/config/steamvr.vrsettings.backup")
                
                dlg.exec()
                
                if QMessageBox.StandardButton.Ok:
                    app.exit()

        except Exception as e:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Virtual Desktop Body Tracking Configurator")            
            dlg.setText(f"Error: {e}")
            
            dlg.exec()
            
            if QMessageBox.StandardButton.Ok:
                app.exit()
            

app = QApplication([])

window = MainWindow()
window.show()

app.exec()


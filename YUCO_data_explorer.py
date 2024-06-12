"""
Read export file from YUCO
Data analysis and associated plot
Export for QGIS applications

Author: Cecile HELLERINGER (2023/09/25)
Modified by Guillaume CHARRIA (2024/05)

YUCO serial number : YUCO-XXXXXXXX

/ comments are in French but can be translated on request /
"""
#%% Definition des variables
chdir = '/home/datawork-lops-oc/YUCO/Python/campagnes_csv'
# Utiliser un chemin absolu

#%% Choix des parametres pour analyse
show = False # True - display all figures on the screen
turb_on = True # Turbidity data/plots
o2_on = True # Oxygen data/plots
stat = False # Print min/max

# temperature_min = 15
# temperature_max = 17
# salinite_min = 37
# salinite_max = 38


#%% Import des librairies
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from RBR_ODO_fct import oxy_compensed,saturation,oxy_uncompensed

#%% Definition espace de travail
os.chdir(chdir)
os.getcwd()

#%% Liste des fichiers de l'espace de travail
files = os.listdir(chdir)
csv = glob.glob('*.csv')
o2_save = o2_on
t_save = turb_on

#%% Boucle sur les fichiers csv presents dans l'espace de travail
for i in range(len(csv)):
    file = csv[i]
    print(file)
    
    #%% Creation repertoire
    if not os.path.exists(os.path.splitext(file)[0]):   
        os.makedirs(os.path.splitext(file)[0])

    #%% Lecture du fichier csv
    df = pd.read_csv(file)
    try: # Depending file versionning
        legato3 = df.dropna(subset=['Legato3 Temperature (�C)'])
    except:
        legato3 = df.dropna(subset=['Legato3 Temperature (C°)'])
    legato3_mission = legato3.loc[legato3['AUV Status']=='MISSION']
    try:
        legato3_mission = legato3_mission.loc[legato3['GPS Coordinates Accepted (Y/N)']=='N']
    except:
        print('---- Ignored due to lack of GPS Coordinates Accepted = N ----')
        continue

    legato3_mission = legato3_mission.loc[legato3['Legato3 Depth (m)']>1]
    columns = list(legato3_mission.columns)
    
    #%% Calculs intermediaires
    time = legato3_mission['Time since startup (s)']
    mon_time = legato3_mission['Legato3 Monotonic time (s)']
    depth = legato3_mission['Legato3 Depth (m)']
    bottom = legato3_mission['Depth (m)'] + legato3_mission['Altitude (m)']
    pressure = legato3_mission['Legato3 Pressure (bar)']
    try: # Depending file versionning
        temperature = legato3_mission['Legato3 Temperature (�C)']
    except:
        temperature = legato3_mission['Legato3 Temperature (C°)']
    conductivite = legato3_mission['Legato3 Conductivity (mS/cm)']
    salinite = legato3_mission['Legato3 Salinity (PSU)']


    if o2_on:
        if not 'Legato3 Oxygen Concentration (umol/L)' in legato3_mission:
            o2_save = o2_on
            o2_on = False
        concentration_oxygene = legato3_mission['Legato3 Oxygen Concentration (umol/L)']
        try: # Depending file versionning
            phase = legato3_mission['Legato3 ODO Phase (�)']
        except:
            phase = legato3_mission['Legato3 ODO Phase (°)']
        try:
            odo_temp = legato3_mission['Legato3 ODO Temperature (C°)']
            odo_t_ok = True
        except:
            odo_t_ok = False

        concentration_oxygene_calcule = oxy_uncompensed(temperature,phase)
        concentration_oxygene_calcule_compensee = oxy_compensed(concentration_oxygene_calcule,pressure,temperature,salinite)
        saturation_oxygene_calcule = saturation(temperature,salinite,concentration_oxygene_calcule_compensee)
    if turb_on:
        if not 'Legato3 Turbidity High (FTU)' in legato3_mission:
            if not 'Legato3 Turbidity (?)' in legato3_mission:
                if not 'Legato3 Turbidity (NTU)' in legato3_mission:
                    t_save = turb_on
                    turb_on = False
        try: # Depending file versionning
            turbidite = legato3_mission['Legato3 Turbidity High (FTU)']
        except:
            try:
               turbidite = legato3_mission['Legato3 Turbidity (?)'] 
            except:
                turbidite = legato3_mission['Legato3 Turbidity (NTU)']


    #%% Visualisation des donnees
    
    #%% Statistiques
    if stat:
        print('temperature min : ',np.min(temperature))
        print('temperature max : ',np.max(temperature))
        print('salinite min : ',np.min(salinite))
        print('salinite max : ',np.max(salinite))
        if o2_on:
            print('concentration oxy min : ',np.min(concentration_oxygene_calcule_compensee))
            print('concentration oxy max : ',np.max(concentration_oxygene_calcule_compensee))
            print('saturation_oxygene_calcule min : ',np.min(saturation_oxygene_calcule))
            print('saturation_oxygene_calcule max : ',np.max(saturation_oxygene_calcule))


    #%% (Temps,Profondeur)_FIGURE_1
    plt.figure()
    fig,ax = plt.subplots()
    ax.plot(time,depth,label='Profondeur Yuko[m]')
    ax.plot(time,bottom,label='Profondeur [m]')
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Profondeur [m]')
    plt.title('Altitude de vol du Yuko par rapport au fond detecte' + '\n'+file)
    ax.invert_yaxis()
    plt.legend()
    plt.grid()
    plt.savefig(os.path.splitext(file)[0]+'/FIG1_TEMPS_PROF.png')
    if show:
        plt.show()
    
    
    #%% (Temps,Profondeur,Temperature)_FIGURE_2
    plt.figure()
    fig,ax = plt.subplots()
    plt.scatter(time,depth,c=temperature,s=8)
    ax.plot(time,bottom,label='Profondeur [m]')
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Profondeur [m]')
    plt.title('Temperature [°C] en fonction de la profondeur au cours du vol'+ '\n'+file)
    ax.invert_yaxis()
    plt.legend()
    plt.grid()
    plt.colorbar()
    plt.savefig(os.path.splitext(file)[0]+'/FIG2_TEMPS_PROF_TEMP.png')
    if show:
        plt.show()
    
    #%% (Temps,Temperature)_FIGURE_3
    plt.figure()
    fig,ax = plt.subplots()
    ax.plot(time,temperature)
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Temperature [°C]')
    plt.title('Temperature donnee par le capteur du Yuko au cours du vol'+ '\n'+file)
    plt.legend()
    plt.grid()
    plt.savefig(os.path.splitext(file)[0]+'/FIG3_TEMPS_TEMP.png')
    if show:
        plt.show()
    
    #%% (Temps,Profondeur,Conductivite)_FIGIRE_4
    plt.figure()
    fig,ax = plt.subplots()
    plt.scatter(time,depth,c=conductivite,s=8)
    ax.plot(time,bottom,label='Profondeur [m]')
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Profondeur [m]')
    plt.title('Conductivite [mS/cm] en fonction de la profondeur au cours du vol'+ '\n'+file)
    ax.invert_yaxis()
    plt.legend()
    plt.grid()
    plt.colorbar()
    plt.savefig(os.path.splitext(file)[0]+'/FIG4_TEMPS_PROF_COND.png')
    if show:
        plt.show()
    
    #%% (Temps,ConductivitÃ©)_FIGURE_5
    plt.figure()
    fig,ax = plt.subplots()
    ax.plot(time,conductivite)
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Conductivite [ms/cm]')
    plt.title('Conductivite donnee par le Legato3 au cours du vol'+ '\n'+file)
    plt.legend()
    plt.grid()
    plt.savefig(os.path.splitext(file)[0]+'/FIG5_TEMPS_COND.png')
    if show:
        plt.show()
    
    #%% (Temps,Profondeur,Oxygene)_FIGURE_6
    if o2_on:
        plt.figure()
        fig,ax = plt.subplots()
        plt.scatter(time,depth,c=concentration_oxygene,s=8)
        ax.plot(time,bottom,label='Profondeur [m]')
        plt.xlabel('Temps depuis le debut du vol [s]')
        plt.ylabel('Profondeur [m]')
        plt.title('Concentration en oxygene [umol/L] en fonction de la profondeur au cours du vol'+ '\n'+file)
        ax.invert_yaxis()
        plt.legend()
        plt.grid()
        plt.colorbar()
        plt.savefig(os.path.splitext(file)[0]+'/FIG6_TEMPS_PROF_OXY.png')
        if show:
            plt.show()
    
        #%% (temps,Oxyne)_FIGURE_7
        plt.figure()
        fig,ax = plt.subplots()
        ax.plot(time,concentration_oxygene)
        plt.xlabel('Temps depuis le debut du vol [s]')
        plt.ylabel('Concentration en oxygene [umol/L]')
        plt.title('Concentration en oxygene [umol/L] donnee par le Legato3 au cours du vol'+ '\n'+file)
        plt.legend()
        plt.grid()
        plt.savefig(os.path.splitext(file)[0]+'/FIG7_TEMPS_OXY.png')
        if show:
            plt.show()

        #%% (Temps,Profondeur,ODO temp)_FIGURE_8
        if odo_t_ok:
            plt.figure()
            fig,ax = plt.subplots()
            plt.scatter(mon_time,depth,c=odo_temp,s=8)
            ax.plot(time,bottom,label='Profondeur [m]')
            plt.xlabel('Temps depuis le debut du vol [s]')
            plt.ylabel('Profondeur [m]')
            plt.title('Temperature [°C] en fonction de la profondeur au cours du vol'+ '\n'+file)
            ax.invert_yaxis()
            plt.legend()
            plt.grid()
            plt.colorbar()
            plt.savefig(os.path.splitext(file)[0]+'/FIG8_TEMPS_PROF_ODOTEMP.png')
            if show:
                plt.show()
        
            #%% (Temps,ODO temp )_FIGURE_9
            plt.figure()
            fig,ax = plt.subplots()
            ax.plot(mon_time,odo_temp)
            plt.xlabel('Temps depuis le debut du vol [s]')
            plt.ylabel('Temperature [°C]')
            plt.title('Temperature donnee par le capteur du Yuko au cours du vol'+ '\n'+file)
            plt.legend()
            plt.grid()
            plt.savefig(os.path.splitext(file)[0]+'/FIG9_TEMPS_ODOTEMP.png')
            if show:
                plt.show()
        
        #%% (Temps,Prof,ODOphase)_FIGURE10
        plt.figure()
        fig,ax = plt.subplots()
        plt.scatter(time,depth,c=phase,s=8)
        ax.plot(time,bottom,label='Profondeur [m]')
        plt.xlabel('Temps depuis le debut du vol [s]')
        plt.ylabel('Profondeur [m]')
        plt.title('Phase [°] en fonction de la profondeur au cours du vol'+ '\n'+file)
        ax.invert_yaxis()
        plt.legend()
        plt.grid()
        plt.colorbar()
        plt.savefig(os.path.splitext(file)[0]+'/FIG10_TEMPS_PROF_ODOPHASE.png')
        if show:
            plt.show()
    
        #%% (Temps,ODOphase )_FIGURE_11
        plt.figure()
        fig,ax = plt.subplots()
        ax.plot(time,phase)
        plt.xlabel('Temps depuis le debut du vol [s]')
        plt.ylabel('Phase [°]')
        plt.title('Phase donnee par le capteur du Yuko au cours du vol'+ '\n'+file)
        plt.legend()
        plt.grid()
        plt.savefig(os.path.splitext(file)[0]+'/F11_PHASE.png')
        if show:
            plt.show()
    
    #%% (Temps,Profondeur,salinite)_FIGURE_12
    plt.figure()
    fig,ax = plt.subplots()
    plt.scatter(time,depth,c=salinite,s=8)
    ax.plot(time,bottom,label='Profondeur [m]')
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Profondeur [m]')
    plt.title('Salinite [PSU] en fonction de la profondeur au cours du vol'+ '\n'+file)
    ax.invert_yaxis()
    plt.legend()
    plt.grid()
    plt.colorbar()
    plt.savefig(os.path.splitext(file)[0]+'/F12_SAL_P.png')
    if show:
        plt.show()
    
    #%% (temps,salinite)_FIGURE_13
    plt.figure()
    fig,ax = plt.subplots()
    ax.plot(time,salinite)
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Salinite [PSU]')
    plt.title('Salinite [PSU] donnee par le Legato3 au cours du vol'+ '\n'+file)
    plt.legend()
    plt.grid()
    plt.savefig(os.path.splitext(file)[0]+'/F13_SAL.png')
    if show:
        plt.show()

    #%% (Temps,Profondeur,turbidite)_FIGURE_14
    if turb_on:
        plt.figure()
        fig,ax = plt.subplots()
        plt.scatter(time,depth,c=turbidite,s=8)
        ax.plot(time,bottom,label='Profondeur [m]')
        plt.xlabel('Temps depuis le debut du vol [s]')
        plt.ylabel('Turbidite [FTU]')
        plt.title('Turbidite [FTU] en fonction de la profondeur au cours du vol'+ '\n'+file)
        ax.invert_yaxis()
        plt.legend()
        plt.grid()
        plt.colorbar()
        plt.savefig(os.path.splitext(file)[0]+'/F14_TURB_P.png')
        if show:
            plt.show()
    
    #%% (temps,salinite)_FIGURE_15
    plt.figure()
    fig,ax = plt.subplots()
    ax.plot(time,turbidite)
    plt.xlabel('Temps depuis le debut du vol [s]')
    plt.ylabel('Turbidite [FTU]')
    plt.title('Turbidite [FTU] donnee par le Legato3 au cours du vol'+ '\n'+file)
    plt.legend()
    plt.grid()
    plt.savefig(os.path.splitext(file)[0]+'/F15_TURB.png')
    if show:
        plt.show()

    #%% (Salinity,Temperature,Profondeur)_FIGURE_16
    plt.figure()
    plt.scatter(salinite,temperature,c=depth,s=8) 
    plt.xlabel('Salinite [PSU]')
    plt.ylabel('Temperature [°C]')
    plt.title('Diagramme (S,T) colore en fonction de la profondeur [m]'+ '\n'+file)
    plt.legend()
    plt.grid()
    plt.colorbar()
    plt.savefig(os.path.splitext(file)[0]+'/FIG16_SAL_TEMP_PROF.png')
    if show:
        plt.show()

    #%% (Temps,Profondeur,Concentration_oxy)_FIGURE_17
    if o2_on:
        plt.figure()
        fig,ax = plt.subplots()
        plt.scatter(time,depth,c=concentration_oxygene_calcule_compensee,s=8) #,vmin=220,vmax=235)
        ax.plot(time,bottom,label='Profondeur [m]')
        plt.xlabel('Temps depuis le debut du vol [s]')
        plt.ylabel('Profondeur [m]')
        plt.title('Concentration en oxygène[umol/L] en fonction de la profondeur au cours du vol'+ '\n'+file)
        ax.invert_yaxis()
        plt.legend()
        plt.grid()
        plt.colorbar()
        plt.savefig(os.path.splitext(file)[0]+'/FIG17_O2COMP.png')
        if show:
            plt.show()

        #%% (Temps,Profondeur,Saturation)_FIGURE_18
        plt.figure()
        fig,ax = plt.subplots()
        plt.scatter(time,depth,c=saturation_oxygene_calcule,s=8) #,vmin =90, vmax=95)
        ax.plot(time,bottom,label='Profondeur [m]')
        plt.xlabel('Temps depuis le debut du vol [s]')
        plt.ylabel('Profondeur [m]')
        plt.title('Saturation oxygène calculé [%] en fonction de la profondeur au cours du vol'+ '\n'+file)
        ax.invert_yaxis()
        plt.legend()
        plt.grid()
        plt.colorbar()
        plt.savefig(os.path.splitext(file)[0]+'/FIG18_O2SAT.png')
        if show:
            plt.show()

    turb_on = t_save # Back to general parameters for next csv file
    o2_on = o2_save # Back to general parameters for next csv file




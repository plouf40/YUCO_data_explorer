"""
Equations de la sonde T.ODO

Helleringer Cécile
06.12.2023

"""

#%% Librairies
import numpy as np

__all__ = ['oxy_uncompensed','oxy_compensed','saturation']
__all__.sort()


#%% Concentration en oxygène non compensée
def oxy_uncompensed(T,P):
    C0 = 0
    C1 = 1.1470973
    C2 = 0
    C3 = 1
    C4 = 8.064644*10**3
    C5 = -123.6473
    C6 = 887.36467*10**(-3)
    C7 = -3.540336*10**(-3)
    C8 = -583.84781
    C9 = 6.133689
    C10 = -23.49897*10**(-3)
    C11 = 46.16926*10**(-6)
    C12 = 16.68928
    C13 = -109.2825*10**(-3)
    C14 = 160.3017*10**(-6)
    C15 = 0
    C16 = -218.08701*10**(-3)
    C17 = 685.75898*10**(-6)
    C18 = 0
    C19 = 0
    C20 = 1.0811971*10**(-3)
    C21 = 0
    C22 = 0
    C23 = 0
    S1 = C4+C5*T+C6*T**2+C7*T**3
    S2 = (C8+C9*T+C10*T**2+C11*T**3)*(C2+C3*P)
    S3 = (C12+C13*T+C14*T**2+C15*T**3)*(C2+C3*P)**2
    S4 = (C16+C17*T+C18*T**2+C19*T**3)*(C2+C3*P)**3
    S5 = (C20+C21*T+C22*T**2+C23*T**3)*(C2+C3*P)**4
    equation = C0 +C1*(S1 + S2 + S3 + S4 + S5)
    return equation

#%% Concentration en oxygène compensée
def oxy_compensed(oxy_un,Press,T,Sal):
    Patm = 10.1325
    C0 = 32*10**(-6)
    GB0 = -6.24097*10**(-3)
    GB1 = -6.93498*10**(-3)
    GB2 = -6.90358*10**(-3)
    GB3 = -4.29155*10**(-3)
    GC0 = -3.11680*10**(-7)
    FCP = 1+ (Press-Patm)*C0
    TS = np.log((298.15-T)/(273.15+T))
    FCS = np.exp(Sal*(GB0+GB1*TS+GB2*TS**2+GB3*TS**3)+GC0*Sal**2)
    equation = oxy_un*FCP*FCS
    return equation

#%% Saturation
def saturation(T,Sal,oxy_co):
    Patm = 10.1325
    GA0 = 2.00856
    GA1 = 3.224
    GA2 = 3.99063
    GA3 = 4.80299
    GA4 = 9.78188*10**(-1)
    GA5 = 1.71069
    GB0 = -6.24097*10**(-3)
    GB1 = -6.93498*10**(-3)
    GB2 = -6.90358*10**(-3)
    GB3 = -4.29155*10**(-3)
    GC0 = -3.11680*10**(-7)
    TS = np.log((298.15-T)/(273.15+T))
    S1 = GB0+GB1*TS+GB2*TS**2+GB3*TS**3
    S2 = GC0*Sal**2+GA0+GA1*TS+GA2*TS**2+GA3*TS**3+GA4*TS**4+GA5*TS**5
    solubility = np.exp(Sal*S1+S2)
    Pvapor = np.exp(52.57-(6690.9/(T+273.15))-4.6818*np.log(T + 273.15))/100
    equation = 2.23916*((10.1325-Pvapor)/(Patm-Pvapor))*oxy_co/solubility
    return equation

# #%% Calculs
# O_u = oxy_uncompensed(T,P)
# O_c = oxy_compensed(O_u,Press,T,Sal)
# O_sat = saturation(T,Sal,O_c)
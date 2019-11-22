import numpy as np
import toml

class AirProperties():
    def __init__(self, c0 = 343.0, rho0 = 1.21, temperature = 20.0, humid = 50.0, p_atm = 101325.0):
        '''
        Set up air properties
        Inputs:
            c0 - sound speed (default 343 m/s - it can be overwriten using standardized calculation)
            rho0 - sound speed (default 1.21 kg/m3 - it can be overwriten using standardized calculation)
            temperature - temperature in degrees (default 20 C)
            humid - relative humidity (default 50 %)
            p_atm - atmospheric pressure (default 101325.0 Pa)
        '''
        # config = load_cfg(config_file)
        self.c0 = np.array(c0, dtype = np.float32)
        self.rho0 = np.array(rho0, dtype = np.float32)
        self.temperature = np.array(temperature, dtype = np.float32)
        self.hr = np.array(humid, dtype = np.float32)
        self.p_atm = np.array(p_atm, dtype = np.float32)

    def standardized_c0_rho0(self,):
        '''
        This method is used to calculate the standardized value of the sound speed and
        air density based on measurements of temperature, humidity and atm pressure.
        It will overwrite the user supplied values
        '''
        # kappla = 0.026
        temp_kelvin = self.temperature + 273.16 # temperature in [K]
        R = 287.031                 # gas constant
        rvp = 461.521               # gas constant for water vapor
        # pvp from Pierce Acoustics 1955 - pag. 555
        pvp = 0.0658 * temp_kelvin**3 - 53.7558 * temp_kelvin**2 \
            + 14703.8127 * temp_kelvin - 1345485.0465
        # Air viscosity
        # vis = 7.72488e-8 * temp_kelvin - 5.95238e-11 * temp_kelvin**2
        # + 2.71368e-14 * temp_kelvin**3
        # Constant pressure specific heat
        cp = 4168.8 * (0.249679 - 7.55179e-5 * temp_kelvin \
            + 1.69194e-7 * temp_kelvin**2 \
            - 6.46128e-11 * temp_kelvin**3)
        cv = cp - R                 # Constant volume specific heat
        # b2 = vis * cp / kappla      # Prandtl number
        gam = cp / cv               # specific heat constant ratio
        # Air density
        self.rho0 = self.p_atm / (R * temp_kelvin) \
            - (1/R - 1/rvp) * self.hr/100 * pvp/temp_kelvin
        # Air sound speed
        self.c0 = (gam * self.p_atm/self.rho0)**0.5

    def air_absorption(self, freq):
        '''
        Calculates the air aborption coefficient in [m^-1]
        '''
        # temp, p0, rh, freqs = self.temp, self.p0, self.rh, self.freqs

        T_0 = 293.15                # Reference temperature [k]
        T_01 = 273.15               # 0 [C] in [k]
        temp_kelvin = self.temperature + 273.15 # Input temp in [k]
        patm_atm = self.p_atm / 101325 # atmosferic pressure [atm]
        F = freq / patm_atm         # relative frequency
        a_ps_ar = np.zeros(F.shape)
        # Saturation pressure
        psat = patm_atm * 10**(-6.8346 * (T_01/temp_kelvin)**1.261 \
            + 4.6151)
        h = patm_atm * self.hr *(psat/patm_atm)
        # Oxygen gas molecule (N2) relaxation frequency
        F_rO = 1/patm_atm * (24 + 4.04 * 10**4 * h * (0.02 + h) \
            / (0.391 + h))
        # Nytrogen gas molecule (N2) relaxation frequency
        F_rN = 1/patm_atm * (T_0/temp_kelvin)**(1/2) * \
            (9 + 280 * h *np.exp(-4.17 * ((T_0/temp_kelvin)**(1/3) - 1)) )
        # Air absorption in [dB/m]
        alpha_ps = 100 * F**2 / patm_atm * (1.84 \
            * 10**(-11) * (temp_kelvin/T_0)**(1/2) \
                + (temp_kelvin/T_0)**(-5/2) \
            * (0.01278 * np.exp(-2239.1/temp_kelvin) \
                / (F_rO + F**2 / F_rO) \
            + 0.1068*np.exp(-3352/temp_kelvin) / (F_rN + F**2 / F_rN)))
        a_ps_ar = alpha_ps * 20 / np.log(10)
        # Air absorption in [1/m]
        self.m = (1/100) * a_ps_ar * patm_atm \
            / (10 * np.log10(np.exp(1)))
        # return self.m

class AlgControls():
    def __init__(self, c0, freq_init = 100.0, freq_end = 10000.0, freq_step = 10):
        '''
        Set up algorithm controls. You set-up your frequency span:
        Inputs:
            freq_init (default - 100 Hz)
            freq_end (default - 10000 Hz)
            freq_step (default - 10 Hz)
        '''
        # config = load_cfg(config_file)
        self.freq_init = np.array(freq_init, dtype = np.float32)
        self.freq_end = np.array(freq_end, dtype = np.float32)
        self.freq_step = np.array(freq_step, dtype = np.float32)
        self.freq = np.arange(self.freq_init, self.freq_end, self.freq_step, dtype = np.float32)
        self.w = 2.0 * np.pi * self.freq
        self.k0 = self.w / c0

### Function to read the .toml file
def load_cfg(cfgfile):
    '''
    This function is used to read configurations from a .toml file
    '''
    with open(cfgfile, 'r') as f:
        config = toml.loads(f.read())
    return config
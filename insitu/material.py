import numpy as np
import matplotlib.pyplot as plt
import warnings
# from insitu.controlsair import load_cfg


class PorousAbsorber():
    def __init__(self, air, controls):
        '''
        Set up a porous absorber. You can model through some formulations such as:
        Delany and Bazley, Johnson, Champoux, Allard, Lafarge, Miki
        '''
        self.c0 = np.float32(air.c0)
        self.rho0 = np.float32(air.rho0)
        self.freq = np.float32(controls.freq)

    def delany_bazley(self, resistivity = 10000.0):
        '''
        This method calculates the Characteristic impedance and the characteristic wave number
        by the Delany and Bazley model
        Inputs:
            resistivity - Flow resistivity
        '''
        self.model = 'Delany and Bazley'
        self.resistivity = resistivity
        X = 1000.0 * self.freq / self.resistivity
        w = 2 * np.pi * self.freq
        k0 = w / self.c0
        self.Zp = np.array((self.rho0 * self.c0) * (1 + 9.08 * X ** (-0.75)
        - 1j * (11.9 * X ** (-0.73))), dtype = np.csingle)
        self.kp = np.array(-1j * k0 * (10.3 * X ** (-0.59) +
            1j * (1 + 10.8 * X ** (-0.7))), dtype = np.csingle)
        # return self.Zp, self.kp

    def miki(self, resistivity = 10000.0):
        '''
        This method calculates the Characteristic impedance and the characteristic wave number
        by the Miki model
        Inputs:
            resistivity - Flow resistivity
        '''
        pass

    def jcal(self, resistivity = 10000.0, porosity = 0.99, tortuosity = 1.01, lam = 300, lam_l = 600):
        '''
        This method calculates the Characteristic impedance and the characteristic wave number
        by the Johnson, Champoux, Allard, Lafarge model
        Inputs:
            resistivity - Flow resistivity
            porosity
            tortuosity
            vischous characteristic lengh (m 10^-6)
            thermal characteristic lengh (m 10^-6)
        '''
        self.model = 'JCAL'
        self.resistivity = np.float32(resistivity)
        self.porosity = np.float32(porosity)
        self.tortuosity = np.float32(tortuosity)
        self.lam = np.float32(lam)
        if lam_l > self.lam:
            self.lam_l = np.float32(lam_l)
        else:
            self.lam_l = 2.0 * self.lam
            print('bla')
            warnings.warn('You provided a thermal characteristic lengh smaller than the viscous characteristic lengh.'+\
            'I took the liberty to fix it for you with the double value.')

        eta = 1.84e-5
        b2 = 0.77
        gamma = 1.4
        p0 = 101320
        v = eta / self.rho0
        v_l = v / b2
        w = 2 * np.pi * self.freq
        # k0 = w / self.c0
        q0 = eta / self.resistivity
        q0_l = self.porosity * (self.lam_l ** 2) / 8.0
        gw = (1 + ((2 * self.tortuosity * q0 / (self.porosity * self.lam)) ** 2) * (1j * w / v)) ** 0.5
        gw_l = (1 + ((self.lam_l / 4) ** 2) * (1j * w / v_l)) ** 0.5
        rho_p = self.rho0 * (self.tortuosity + ((v * self.porosity) / (1j * w * q0)) * gw)
        kappa_p = gamma * p0 / (gamma - ((gamma - 1.0) / (1 + ((v_l * self.porosity) / (1j * w * q0_l)) * gw_l)))
        self.Zp = (rho_p * kappa_p) ** 0.5
        self.kp = w * ((rho_p / kappa_p) ** 0.5)

    def layer_over_rigid(self, thickness = 25.0/1000, theta = 0.0):
        '''
        This method calculates the surface impedance and the associated reflection and 
        absorption coefficient - for a layer over a rigid backing
        Inputs:
            thickness [m] (default 25 [mm])
            theta [deg] - incidence angle (default 0 [deg] - normal incidence)
        '''
        self.thickness = np.float32(thickness)
        self.theta = np.radians(theta)
        self.material_scene = 'locally reactive, sample over rigid backing; thickness: '+\
            "{:.2f}".format(self.thickness) + ' [m]'
        self.Zs = -1j * self.Zp * (1 / np.tan(self.kp * self.thickness)) #FixMe - correct Zs for other angles
        self.Vp = (self.Zs * np.cos(self.theta) - self.rho0 * self.c0) /\
            (self.Zs * np.cos(self.theta) + self.rho0 * self.c0)
        self.alpha = 1 - (np.abs(self.Vp)) ** 2.0
        # return self.Zs, self.Vp, self.alpha

    def plot_zc(self,):
        '''
        This method is used to plot the reference characteristic impedance
        '''
        pass

    def plot_kc(self,):
        '''
        This method is used to plot the reference characteristic wave number
        '''
        pass

    def plot_zs(self,):
        '''
        This method is used to plot the reference surface impedance
        '''
        pass

    def plot_vp(self,):
        '''
        This method is used to plot the reference reflection coefficient
        '''
        pass

    def plot_absorption(self):
        '''
        This method is used to plot the reference absorption coefficient
        '''
        fig = plt.figure()
        fig.canvas.set_window_title(self.material_scene)
        plt.plot(self.freq, self.alpha, 'k-', label=self.model)
        plt.title(self.material_scene)
        plt.grid(linestyle = '--', which='both')
        plt.xscale('log')
        plt.legend(loc = 'lower right')
        plt.xticks([50, 100, 500, 1000, 5000, 10000],
            ['50', '100', '500', '1000', '5000', '10000'])
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('absorption coefficient [-]')
        plt.ylim((-0.2, 1.2))
        plt.xlim((0.8 * self.freq[0], 1.2*self.freq[-1]))
        plt.show()



# class PorousAbsorber():
#     def __init__(self, config_file, air, freq):
#         '''
#         Set up porous absorber
#         '''
#         self.c0 = np.float32(air.c0)
#         self.rho0 = np.float32(air.rho0)
#         self.freq = freq
#         config = load_cfg(config_file)
#         self.resistivity = np.float32(config['porous']['resistivity'])
#         self.porosity = np.float32(config['porous']['porosity'])
#         self.tortuosity = np.float32(config['porous']['tortuosity'])
#         self.lam = np.float32(config['porous']['lam'])
#         self.lam_l = np.float32(config['porous']['lam_l'])
#         # self.thickness = config['porous']['resistivity']

#     def delany_bazley(self):
#         self.model = 'Delany and Bazley'
#         X = 1000.0 * self.freq / self.resistivity
#         w = 2 * np.pi * self.freq
#         k0 = w / self.c0
#         self.Zp = np.array((self.rho0 * self.c0) * (1 + 9.08 * X ** (-0.75)
#         - 1j * (11.9 * X ** (-0.73))), dtype = np.csingle)
#         self.kp = np.array(-1j * k0 * (10.3 * X ** (-0.59) +
#             1j * (1 + 10.8 * X ** (-0.7))), dtype = np.csingle)
#         return self.Zp, self.kp

#     def jcal(self):
#         self.model = 'JCAL'
#         eta = 1.84e-5
#         b2 = 0.77
#         gamma = 1.4
#         p0 = 101320
#         v = eta / self.rho0
#         v_l = v / b2
#         w = 2 * np.pi * self.freq
#         k0 = w / self.c0
#         q0 = eta / self.resistivity
#         q0_l = self.porosity * (self.lam_l ** 2) / 8.0
#         gw = (1 + ((2 * self.tortuosity * q0 / (self.porosity * self.lam)) ** 2) * (1j * w / v)) ** 0.5
#         gw_l = (1 + ((self.lam_l / 4) ** 2) * (1j * w / v_l)) ** 0.5
#         rho_p = self.rho0 * (self.tortuosity + ((v * self.porosity) / (1j * w * q0)) * gw)
#         kappa_p = gamma * p0 / (gamma - ((gamma - 1.0) / (1 + ((v_l * self.porosity) / (1j * w * q0_l)) * gw_l)))
#         self.Zp = (rho_p * kappa_p) ** 0.5
#         self.kp = w * ((rho_p / kappa_p) ** 0.5)
#         # rhop = self.rho0 * self.tortuosity * (1 +
#         #     ((self.resistivity * self.porosity) / (1j * self.tortuosity * self.rho0 * w)) *
#         #     ((1 + (4 * 1j * (self.tortuosity ** 2) * eta *self.rho0 * w) /
#         #     ((self.resistivity ** 2) * (self.lam ** 2) * (self.porosity ** 2))) ** 0.5))
#         # kappa_p = gamma * p0 / (gamma - ((gamma - 1.0) / (1 + ((self.resistivity * self.porosity) /
#         # (1j * self.tortuosity * self.rho0 * b2 * w)) * ((1 + (4 * 1j * (self.tortuosity ** 2) * eta *self.rho0 * b2 * w) /
#         #     ((self.resistivity ** 2) * (self.lam ** 2) * (self.porosity ** 2))) ** 0.5)

#     def layer_over_rigid(self, thickness):
#         self.Zs = -1j * self.Zp * (1 / np.tan(self.kp * thickness))
#         self.Vp = (self.Zs - self.rho0 * self.c0) / (self.Zs + self.rho0 * self.c0)
#         self.alpha = 1 - (np.abs(self.Vp)) ** 2.0
#         return self.Zs, self.Vp, self.alpha

#     def plot_absorption(self):
#         plt.figure()
#         plt.plot(self.freq, self.alpha, 'k-', label=self.model)
#         plt.title('Porous material layer over rigid backing')
#         plt.grid(linestyle = '--', which='both')
#         plt.xscale('log')
#         plt.legend(loc = 'lower right')
#         plt.xticks([50, 100, 500, 1000, 5000, 10000],
#             ['50', '100', '500', '1000', '5000', '10000'])
#         plt.xlabel('Frequency [Hz]')
#         plt.ylabel('absorption coefficient [-]')
#         plt.ylim((-0.2, 1.2))
#         plt.xlim((0.8 * self.freq[0], 1.2*self.freq[-1]))
#         plt.show()
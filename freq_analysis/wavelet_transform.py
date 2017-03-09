"""

Short rewriting of the wavelet transform module of SciPy

correspondance: yann.zerlaut@iit.it

"""

import numpy as np
from scipy import signal

def ricker(t, f, t0):
    """
    Ricker wavelet of frequency 'f' centered in t0 and  over and signal length.
    """
    fact = (np.pi**2) * (f**2) * ((t - t0)**2)
    y = (1.0 - 2.0 * fact) * np.exp(-fact)
    return y

def make_ricker_of_right_size(freq, dt, with_t=False, factor_freq=2.):
    """
    returns a ricker of size int(factor_freq*/(freq*dt))
    centered in the middle of the array (for use with convolve)

    Note factor_freq = 2 covers well the extent of the ricker
    """
    tstop = factor_freq/freq
    t = np.arange(int(tstop/dt))*dt
    if with_t:
        return t, ricker(t, freq, t[-1]/2.)
    else:
        return ricker(t, freq, t[-1]/2.) 
    
def my_cwt(data, frequencies, dt):
    """
    Continuous wavelet transform, adapted from:
    https://github.com/scipy/scipy/blob/v0.18.1/scipy/signal/wavelets.py#L311-L365

    Performs a continuous wavelet transform on `data`,
    using the `wavelet` function. A CWT performs a convolution
    with `data` using the `wavelet` function, which is characterized
    by a frequency parameter.

    Parameters
    ----------
    data : (N,) ndarray
        data on which to perform the transform.
    frequencies : (M,) sequence
        Widths to use for transform.
    Returns
    -------
    cwt: (M, N) ndarray
        Will have shape of (len(frequencies), len(data)).
                                    width[ii]), mode='same')
    """
    output = np.zeros([len(frequencies), len(data)])
    for ind, freq in enumerate(frequencies):
        wavelet_data = make_ricker_of_right_size(freq, dt)
        conv_number = signal.convolve(np.ones(len(data)), np.ones(len(wavelet_data)),
                                      mode='same')
        sliding_mean = signal.convolve(data, np.ones(len(wavelet_data)),
                                       mode='same')/conv_number
        output[ind, :] = signal.convolve(data-sliding_mean, wavelet_data,
                                         mode='same')/conv_number
    return output/dt

def illustration_plot(t, data, coefs, dt, tstop, freq1, freq2, freq3):
    """
    a plot to illustrate the output of the wavelet analysis
    """
    fig = plt.figure(figsize=(12,6))
    plt.subplots_adjust(wspace=.8, hspace=.5, bottom=.2)
    # signal plot
    plt.subplot2grid((3, 8), (0,0), colspan=6)
    plt.plot(1e3*t, data, lw=2)
    plt.ylabel('signal')
    for f, tt in zip([freq2, freq1, freq3], [200,500,800]):
        plt.annotate(str(int(f))+'Hz', (tt, data.max()))
    plt.xlim([1e3*t[0], 1e3*t[-1]])
    # time frequency power plot
    ax1 = plt.subplot2grid((3, 8), (1,0), rowspan=2, colspan=6)
    c = plt.contourf(1e3*t, freqs, coefs, cmap='PRGn', aspect='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('frequency (Hz)')
    plt.yticks([10, 40, 70, 100]);
    # inset with legend
    acb = plt.axes([.4, .4, .02, .2])
    plt.colorbar(c, cax=acb, label='coeffs (a.u.)', ticks=[0])
    # mean power plot over intervals
    plt.subplot2grid((3, 8), (1, 6), rowspan=2)
    for t1, t2 in zip([0,300e-3,700e-3], [300e-3,700e-3, 1000e-3]):
        cond = (t>t1) & (t<t2)
        plt.barh(freqs, np.power(coefs[:,cond],2).mean(axis=1)*dt,\
                 label='t$\in$['+str(int(1e3*t1))+','+str(int(1e3*t2))+']')
    plt.legend(prop={'size':'small'}, loc=(0.1,1.1))
    plt.yticks([10, 40, 70, 100]);
    plt.xlabel(' mean \n power')
    # max of power over intervals
    plt.subplot2grid((3, 8), (1, 7), rowspan=2)
    for t1, t2 in zip([0,300e-3,600e-3], [300e-3,600e-3, 1000e-3]):
        cond = (t>t1) & (t<t2)
        plt.barh(freqs, np.power(coefs[:,cond],2).max(axis=1)*dt,\
                 label='t$\in$['+str(int(1e3*t1))+','+str(int(1e3*t2))+']')
    plt.yticks([10, 40, 70, 100]);
    plt.xlabel(' max. \n power');
    return fig

if __name__ == '__main__':

    import numpy as np
    import matplotlib.pylab as plt

    plt.style.use('ggplot')
    # temporal sampling
    dt, tstop = 1e-4, 1.
    t = np.arange(int(tstop/dt))*dt

    # ### artificially generated signal, transient oscillations
    freq1, width1, freq2, width2, freq3, width3 = 10., 100e-3, 40., 40e-3, 70., 20e-3
    data  = 50+np.cos(2*np.pi*freq1*t)*np.exp(-(t-.5)**2/2./width1**2)+\
            np.cos(2*np.pi*freq2*t)*np.exp(-(t-.2)**2/2./width2**2)+\
            np.cos(2*np.pi*freq3*t)*np.exp(-(t-.8)**2/2./width3**2)
    
    # ### adding colored noise to test robustness
    nl = 0e-2 # noise level
    data += nl*np.convolve(np.exp(-np.arange(1000)*dt/400e-3),\
                        np.random.randn(len(t)), mode='same') # a slow one
    data += nl*np.convolve(np.exp(-np.arange(1000)*dt/5e-3),\
                        np.random.randn(len(t)), mode='same') # a faster one

    # Continuous Wavelet Transform analysis
    freqs = np.linspace(1, 90, 1e2)
    coefs = my_cwt(data, freqs, dt)

    illustration_plot(t, data, coefs, dt, tstop, freq1, freq2, freq3)
    plt.show()

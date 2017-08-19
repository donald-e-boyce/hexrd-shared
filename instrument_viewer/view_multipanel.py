import numpy as np
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

from hexrd.gridutil import cellIndices
from hexrd import imageseries
from make_pd_patch import PolarView

from skimage import io
from skimage import transform as tf
from skimage.exposure import equalize_adapthist

Pimgs = imageseries.process.ProcessedImageSeries

from display_plane import DisplayPlane

class InstrumentViewer(object):

    def __init__(self, instr, ims, planeData):
        self.planeData = planeData
        self.instr = instr
        self._load_panels()
        self._load_images(ims)
        self.dplane = DisplayPlane()
        self.pixel_size = 0.5
        self._make_dpanel()

        self._figure, self._axes = plt.subplots()
        plt.subplots_adjust(right=0.6)
        self._cax = None
        self._active_panel_id = None
        self.active_panel_mode = False
        self.polar_mode = False
        self.image = None
        self.have_rings = False
        self.ring_plots = []
        self.slider_delta = 10.0
        self.set_interactors()
        self.show_image()
        plt.show()

    # ========== Set up
    def _load_panels(self):
        self.panel_ids = self.instr._detectors.keys()
        self.panels = self.instr._detectors.values()

        # save original panel parameters for reset
        self.panel_vecs_orig = dict()
        for pid in self.panel_ids:
            p = self.instr._detectors[pid]
            self.panel_vecs_orig[pid] = (p.tvec, p.tilt)

    def _load_images(self, ims):
        # load images from imageseries
        # ... add processing here
        print "loading images"
        m = ims.metadata
        pids = m['panels']
        d = dict(zip(pids, range(len(pids))))

        if 'process' in m:
            pspec = m['process']
            ops = []
            for p in pspec:
                k = p.keys()[0]
                ops.append((k, p[k]))
            pims = Pimgs(ims, ops)
        else:
            pims = ims

        self.images = []
        self.image_dict = dict()
        for pid in self.panel_ids:
            this_img = pims[d[pid]]
            self.images.append(this_img)
            self.image_dict[pid] = this_img

    def _make_dpanel(self):
        self.dpanel_sizes = self.dplane.panel_size(self.instr)
        self.dpanel = self.dplane.display_panel(self.dpanel_sizes,
                                                self.pixel_size)

    # ========== GUI
    def set_interactors(self):
        self._figure.canvas.mpl_connect('key_press_event', self.onkeypress)

        # sliders
        axcolor = 'lightgoldenrodyellow'

        # . translations
        self.tx_ax = plt.axes([0.65, 0.65, 0.30, 0.03], axisbg=axcolor)
        self.ty_ax = plt.axes([0.65, 0.60, 0.30, 0.03], axisbg=axcolor)
        self.tz_ax = plt.axes([0.65, 0.55, 0.30, 0.03], axisbg=axcolor)

        # . tilts
        self.gx_ax = plt.axes([0.65, 0.50, 0.30, 0.03], axisbg=axcolor)
        self.gy_ax = plt.axes([0.65, 0.45, 0.30, 0.03], axisbg=axcolor)
        self.gz_ax = plt.axes([0.65, 0.40, 0.30, 0.03], axisbg=axcolor)

        self._active_panel_id = self.panel_ids[0]
        panel = self.instr._detectors[self._active_panel_id]
        self._make_sliders(panel)

        # radio button (panel selector)
        rd_ax = plt.axes([0.65, 0.70, 0.30, 0.15], axisbg=axcolor)
        self.radio_panels = RadioButtons(rd_ax, self.panel_ids)
        self.radio_panels.on_clicked(self.on_change_panel)

    def _make_sliders(self, panel):
        """make sliders for given panel"""
        t = panel.tvec
        d = self.slider_delta

        g = np.degrees(panel.tilt)

        # translations
        self.tx_ax.clear()
        self.ty_ax.clear()
        self.tz_ax.clear()

        self.slider_tx = Slider(self.tx_ax, 't_x', t[0] - d, t[0] + d,
                                valinit=t[0])
        self.slider_ty = Slider(self.ty_ax, 't_y', t[1] - d, t[1] + d,
                                valinit=t[1])
        self.slider_tz = Slider(self.tz_ax, 't_z', t[2] - d, t[2] + d,
                                valinit=t[2])

        self.slider_tx.on_changed(self.update)
        self.slider_ty.on_changed(self.update)
        self.slider_tz.on_changed(self.update)

        # tilts
        self.gx_ax.clear()
        self.gy_ax.clear()
        self.gz_ax.clear()

        self.slider_gx = Slider(self.gx_ax, r'$\gamma_x$', g[0] - d, g[0] + d,
                                valinit=g[0])
        self.slider_gy = Slider(self.gy_ax, r'$\gamma_y$', g[1] - d, g[1] + d,
                                valinit=g[1])
        self.slider_gz = Slider(self.gz_ax, r'$\gamma_z$', g[2] - d, g[2] + d,
                                valinit=g[2])

        self.slider_gx.on_changed(self.update)
        self.slider_gy.on_changed(self.update)
        self.slider_gz.on_changed(self.update)


    # ========================= Properties
    @property
    def active_panel(self):
        return self.instr._detectors[self._active_panel_id]

    @property
    def instrument_output(self):
        tmpl = "new-instrument-%s.yml"
        if not hasattr(self, '_ouput_number'):
            self._ouput_number = 0
        else:
            self._ouput_number += 1

        return tmpl % self._ouput_number

    # ========================= Event Responses

    def onkeypress(self, event):
        #
        # r : reset panels
        # w : write instrument settings
        # += : increase slider deltas
        # -_ : decrease slider deltas
        # q : quit
        #
        print 'key press event: %s' % event.key
        if event.key in 'a':
            self.active_panel_mode = not self.active_panel_mode
            print "active panel mode is: %s" % self.active_panel_mode
        elif event.key in 'r':
            # Reset
            print "resetting panels"
            self.reset_panels()
        elif event.key in 'w':
            # Write config
            print "writing instrument config file"
            self.instr.write_config(self.instrument_output)
        elif event.key in '+=':
            # increase slider delta
            print "increasing slider delta"
            self.slider_delta *= 1.5
            self.on_change_panel(self._active_panel_id)
        elif event.key in '-_':
            print "decreasing slider delta"
            # decrease slider delta
            self.slider_delta /= 1.5
            self.on_change_panel(self._active_panel_id)
        elif event.key in 'm':
            # toggle polar mode for viewing rings
            print "switching image mode"
            self.toggle_polar()
        elif event.key in 'qQ':
            print "quitting"
            plt.close('all')
            return
        else:
            print("unrecognized key = %s\n" % event.key)

        self.show_image()

    def on_change_panel(self, id):
        self._active_panel_id = id
        panel = self.instr._detectors[id]
        self._make_sliders(panel)
        self.update(0)

    def toggle_polar(self):
        self.polar_mode = not self.polar_mode
        self.clear_rings()

    def reset_panels(self):
        # in active_panel_mode, only reset active panel; otherwise reset all
        if self.active_panel_mode:
            tt = self.panel_vecs_orig[self._active_panel_id]
            self.active_panel.tvec = tt[0]
            self.active_panel.tilt = tt[1]
        else:
            for pid in self.panel_ids:
                p = self.instr._detectors[pid]
                tt = self.panel_vecs_orig[pid]
                p.tvec = tt[0]
                p.tilt = tt[1]

        self._make_sliders(self.active_panel)
        self.show_image()

    def update(self, val):
        panel = self.instr._detectors[self._active_panel_id]

        tvec = panel.tvec
        tvec[0] = self.slider_tx.val
        tvec[1] = self.slider_ty.val
        tvec[2] = self.slider_tz.val
        panel.tvec = tvec

        tilt = panel.tilt
        tilt[0] = np.radians(self.slider_gx.val)
        tilt[1] = np.radians(self.slider_gy.val)
        tilt[2] = np.radians(self.slider_gz.val)
        panel.tilt = tilt

        self.show_image()

    # ========== Drawing
    def draw_polar(self):
        """show polar view of rings"""
        pv = PolarView(self.planeData, self.instr)
        wimg = pv.warp_image(self.image_dict)
        self._axes.set_title("Instrument")
        self.plot_dplane(warped=wimg)
        self._axes.axis('image')

    def show_image(self):
        # self._axes.clear()
        if self.polar_mode:
            self.draw_polar()
        else:
            self._axes.set_title("Instrument")
            self.plot_dplane()
        self.addrings()

        # # colorbar
        # # cax = ax.imshow(np.log(1+ self._ims[k]))
        # del self._cax
        # self._cax = ax.imshow(self._ims[k])
        # if hasattr(self, 'cb'):
        #     self.cb.remove()
        # self.cb = fig.colorbar(self._cax)
        # self.cb.set_label('Some Units')
        plt.draw()

    def addrings(self):
        self.ring_data = []
        if not self.have_rings:
            # generate and save rings
            dp = self.dpanel
            ring_angs, ring_xys = dp.make_powder_rings(
                self.planeData, delta_eta=1)
            if self.polar_mode:
                colorspec = 'c-'
                pv = PolarView(self.planeData, self.instr)
                ringtth = [a[0,0] for a in ring_angs]
                rings2plot = []
                for tth in ringtth:
                    px = pv.tth_to_pixel(tth)
                    ext = pv.neta
                    self.ring_data.append(np.array([[0, px], [ext, px]]))

            else:
                colorspec = 'c.'
                for ring in ring_xys:
                    self.ring_data.append(dp.cartToPixel(ring))
            self.have_rings = True

            self.ring_plots = []
            for pr in self.ring_data:
                self.ring_plots += self._axes.plot(pr[:, 1], pr[:, 0], colorspec, ms=4)

    def clear_rings(self):
        for r in self.ring_plots:
            r.remove()
        self.have_rings = False

    def plot_dplane(self, warped=None):
        dpanel = self.dpanel
        nrows_map = dpanel.rows
        ncols_map = dpanel.cols

        if warped is None:
            warped = np.zeros((nrows_map, ncols_map))
            for i in range(len(self.images)):
                detector_id = self.panel_ids[i]
                if self.active_panel_mode:
                    if not detector_id == self._active_panel_id:
                        continue

                img = self.images[i]
                panel = self.instr._detectors[detector_id]

                # map corners
                corners = np.vstack(
                    [panel.corner_ll,
                     panel.corner_lr,
                     panel.corner_ur,
                     panel.corner_ul,
                     ]
                )
                mp = panel.map_to_plane(corners, self.dplane.rmat, self.dplane.tvec)

                col_edges = dpanel.col_edge_vec
                row_edges = dpanel.row_edge_vec
                j_col = cellIndices(col_edges, mp[:, 0])
                i_row = cellIndices(row_edges, mp[:, 1])

                src = np.vstack([j_col, i_row]).T
                dst = panel.cartToPixel(corners, pixels=True)
                dst = dst[:, ::-1]

                tform3 = tf.ProjectiveTransform()
                tform3.estimate(src, dst)

                warped += tf.warp(img, tform3,
                                  output_shape=(self.dpanel.rows,
                                                self.dpanel.cols))
            img = equalize_adapthist(warped, clip_limit=0.05, nbins=2**16)
        else:
            img = warped
            #img = equalize_adapthist(warped/np.amax(warped), clip_limit=0.5, nbins=2**16)


        mycmap = plt.cm.plasma
        if self.image is None:
            self.image = self._axes.imshow(
                    img, cmap=mycmap,
                    vmax=None,
                    interpolation="none")
        else:
            shp = img.shape

            self.image.set_data(img)
            self.image.set_clim(vmax=np.amax(img))
            self._figure.canvas.draw()
            self.image.set_extent([0, shp[1], shp[0], 0]) # l, r, b, t
        self._axes.format_coord = self.format_coord

    def format_coord(self, j, i):
        """
        i, j are col, row
        """
        xy_data = self.dpanel.pixelToCart(np.vstack([i, j]).T)
        ang_data, gvec = self.dpanel.cart_to_angles(xy_data)
        tth = ang_data[:, 0]
        eta = ang_data[:, 1]
        dsp = 0.5 *self. planeData.wavelength / np.sin(0.5*tth)
        hkl = str(self.planeData.getHKLs(asStr=True, allHKLs=True, thisTTh=tth))
        return "x=%.2f, y=%.2f, d=%.3f\ntth=%.2f eta=%.2f HKLs=%s" \
          % (xy_data[0, 0], xy_data[0, 1], dsp, np.degrees(tth), np.degrees(eta), hkl)

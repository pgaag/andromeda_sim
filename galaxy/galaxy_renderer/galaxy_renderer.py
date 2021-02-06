"""
OpenGL output for gravity simulation
"""
#
# Copyright (C) 2017  "Peter Roesch" <Peter.Roesch@fh-augsburg.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# or open http://www.fsf.org/licensing/licenses/gpl.html
#
import sys
import time

try:
    from OpenGL import GLUT
    from OpenGL import GL
    from OpenGL import GLU
except ImportError:
    print(' Error: Software not installed properly !!')
    sys.exit()

from galaxy.galaxy_renderer.mouse_interactor import MouseInteractor
from galaxy.galaxy_renderer.simulation_constants import END_MESSAGE


# initial window parameters
_WINDOW_SIZE = (1280, 1280)
_WINDOW_POSITION = (100, 100)
_LIGHT_POSITION = (2, 2, 3)
_CAMERA_POSITION = (0, 0, 2)


class GalaxyRenderer:
    """
        Class containing OpenGL code
    """

    def __init__(self, render_pipe, fps):
        self.render_pipe = render_pipe
        self.fps = fps
        self.bodies = None
        self.do_exit = False
        self.sphere = None
        self.init_glut()
        self.init_gl()
        self.mouse_interactor = MouseInteractor(0.01, 1)
        self.mouse_interactor.register_callbacks()

    def init_glut(self):
        """
            Set up window and main callback functions
        """
        GLUT.glutInit(['Galaxy Renderer'])
        GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGB)
        GLUT.glutInitWindowSize(_WINDOW_SIZE[0], _WINDOW_SIZE[1])
        GLUT.glutInitWindowPosition(_WINDOW_POSITION[0], _WINDOW_POSITION[1])
        GLUT.glutCreateWindow(str.encode("Galaxy Renderer"))
        GLUT.glutDisplayFunc(self.render)
        GLUT.glutIdleFunc(self.update_positions)

    def init_gl(self):
        """
            Initialise OpenGL settings
        """
        self.sphere = GL.glGenLists(1)
        GL.glNewList(self.sphere, GL.GL_COMPILE)
        quad_obj = GLU.gluNewQuadric()
        GLU.gluQuadricDrawStyle(quad_obj, GLU.GLU_FILL)
        GLU.gluQuadricNormals(quad_obj, GLU.GLU_SMOOTH)
        GLU.gluSphere(quad_obj, 1, 16, 16)
        GL.glEndList()
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_LIGHTING)
        # make sure normal vectors of scaled spheres are normalised
        GL.glEnable(GL.GL_NORMALIZE)
        GL.glEnable(GL.GL_LIGHT0)
        light_pos = list(_LIGHT_POSITION) + [1]
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, light_pos)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT, [0.7, .7, .7, 1])
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE, [0.7, 0.7, 0.7, 1])
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, [0.1, 0.1, 0.1, 1])
        GL.glMaterialf(GL.GL_FRONT, GL.GL_SHININESS, 20)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(60, 1, .01, 10)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def render(self):
        """
            Render the scene using the sphere display list
        """
        if self.do_exit:
            print('renderer exiting ...')
            # glut event loop needs hard exit ...
            # sys.exit(1)
            quit()

        if self.bodies is None:
            time.sleep(1 / self.fps)
            return
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        x_size = GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH)
        y_size = GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT)
        GLU.gluPerspective(60, float(x_size) / float(y_size), 0.05, 10)  # Zoomfaktor am Anfang
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslatef(-_CAMERA_POSITION[0],
                        -_CAMERA_POSITION[1],
                        -_CAMERA_POSITION[2])
        self.mouse_interactor.apply_transformation()
        for body_index in range(self.bodies.shape[0]):
            body = self.bodies[body_index, :]
            GL.glPushMatrix()
            GL.glTranslatef(body[0], body[1], body[2])  # Ausrichtung
            GL.glScalef(body[3], body[3], body[3])
            if len(body) == 8:
                GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                                body[4:])
            GL.glCallList(self.sphere)
            GL.glPopMatrix()
        GLUT.glutSwapBuffers()

    @staticmethod
    def start():
        """
            Start the GLUT event loop.
        """
        GLUT.glutMainLoop()

    def update_positions(self):
        """
            Read new object positions from pipe.
        """
        if self.render_pipe.poll():
            pipe_input = self.render_pipe.recv()
            if isinstance(pipe_input, str) and pipe_input == END_MESSAGE:
                self.do_exit = True
            else:
                self.bodies = pipe_input
                GLUT.glutPostRedisplay()
        else:
            time.sleep(1 / self.fps)


def startup(render_pipe, fps):
    """
        Create GalaxyRenderer instance and start rendering

        Args:
            render_pipe (multiprocessing.Pipe): Pipe to read positions from
            fps (float): Number of frames per second
    """
    print('creating renderer')
    galaxy_renderer = GalaxyRenderer(render_pipe, fps)
    print('starting renderer')
    galaxy_renderer.start()
    print('done')

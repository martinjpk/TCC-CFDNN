import gmsh

class Mesh():
    def __init__(self, name, dat_path, dr, br, dim, debug=False):
        gmsh.initialize()
        gmsh.model.add(name)
        # gmsh.option.setNumber("General.Terminal", 1)
        # gmsh.option.setNumber('General.AbortOnError', 2)
        self.dr = dr
        self.br = br
        self.dim = dim
        self.name = name
        self.debug = debug
        self.dat_path = dat_path

    def set_box_res(self, res):
        self.br = res

    def set_dat_res(self, res):
        self.dr = res

    def _read_dat(self, dat_path):
        with open(dat_path, 'r') as f:
            _, upper, lower = f.read().split('\n\n')
        return self._get_points(upper), self._get_points(lower)

    def _get_points(self, data):
        return [tuple(map(float, x.split())) for x in data.split('\n') if x!='']

    def genPoints(self):
        tmp = gmsh.model.getCurrent()
        gmsh.model.setCurrent(self.name)
        geo = gmsh.model.geo
        box = [
            geo.addPoint(.5-self.dim[0]/2, 0-self.dim[1]/2, 0, self.br),
            geo.addPoint(.5+self.dim[0]/2, 0-self.dim[1]/2, 0, self.br), 
            geo.addPoint(.5+self.dim[0]/2, 0+self.dim[1]/2, 0, self.br),
            geo.addPoint(.5-self.dim[0]/2, 0+self.dim[1]/2, 0, self.br)
        ]
        box = [geo.addLine(a, b) for a, b in zip(box, box[1:]+[box[0]])]
        uppts, dwpts = self._read_dat(self.dat_path)
        p0, p1 = uppts[0], uppts[-1]
        p0, p1 = geo.addPoint(*p0, 0, self.dr), geo.addPoint(*p1, 0, self.dr)
        upspl = [geo.addPoint(x, y, 0, self.dr) for x, y in uppts[1:-1]]
        dwspl = [geo.addPoint(x, y, 0, self.dr) for x, y in dwpts[1:-1]]
        spl = [
             geo.addSpline([p0]+dwspl+[p1]),
            -geo.addSpline([p0]+upspl+[p1])
        ]
        bx = geo.addCurveLoop(box)
        sp = geo.addCurveLoop(spl)
        geo.addPlaneSurface([bx, sp])
        geo.synchronize()
        gmsh.model.mesh.generate(2)
        gmsh.model.setCurrent(tmp)
    
    def write(self, save_file):
        tmp = gmsh.model.get_current()
        gmsh.model.set_current(self.name)
        gmsh.write(save_file)
        gmsh.model.set_current(tmp)
    

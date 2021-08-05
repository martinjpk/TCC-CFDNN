import gmsh

class Mesh():
    def __init__(self, name, dat_path, size_af, size_ff, dim, debug=False):
        gmsh.initialize()
        gmsh.model.add(name)
        # gmsh.option.setNumber("General.Terminal", 1)
        # gmsh.option.setNumber('General.AbortOnError', 2)
        self.raf = size_af
        self.rff = size_ff
        self.dim = dim
        self.name = name
        self.debug = debug
        self.dat_path = dat_path
        self.ff_shape = 'circle'
        self.ff_shape_ = {'box': self.__make_box, 'circle': self.__make_circle}

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

    def __make_box(self, geo, center, dim, res):
        box = [
            geo.addPoint(center[0]-dim[0]/2, center[1]-dim[1]/2, 0, res),
            geo.addPoint(center[0]+dim[0]/2, center[1]-dim[1]/2, 0, res), 
            geo.addPoint(center[0]+dim[0]/2, center[1]+dim[1]/2, 0, res),
            geo.addPoint(center[0]-dim[0]/2, center[1]+dim[1]/2, 0, res)
        ]
        return [geo.addLine(p, box[(i+1)%4]) for i, p in enumerate(box)]

    def __make_circle(self, geo, center, rad, res):
        c = geo.addPoint(*center, 0)
        circle = [
            geo.addPoint(center[0], center[1]+rad, 0, res),
            geo.addPoint(center[0]+rad, center[1], 0, res),
            geo.addPoint(center[0], center[1]-rad, 0, res),
            geo.addPoint(center[0]-rad, center[1], 0, res)
        ]
        return [geo.addCircleArc(p, c, circle[(i+1)%4]) for i, p in enumerate(circle)]

    def genPoints(self):
        tmp = gmsh.model.getCurrent()
        gmsh.model.setCurrent(self.name)
        geo = gmsh.model.geo
        ff = self.ff_shape_[self.ff_shape](geo, [.5, 0], self.dim, self.rff)
        uppts, dwpts = self._read_dat(self.dat_path)
        p0, p1 = uppts[0], uppts[-1]
        p0, p1 = geo.addPoint(*p0, 0, self.raf), geo.addPoint(*p1, 0, self.raf)
        upspl = [geo.addPoint(x, y, 0, self.raf) for x, y in uppts[1:-1]]
        dwspl = [geo.addPoint(x, y, 0, self.raf) for x, y in dwpts[1:-1]]
        af = [
             geo.addSpline([p0]+dwspl+[p1]),
            -geo.addSpline([p0]+upspl+[p1])
        ]
        ff = geo.addCurveLoop(ff,1)
        af = geo.addCurveLoop(af,2)
        geo.addPlaneSurface([ff, af])
        geo.synchronize()
        farfield = gmsh.model.addPhysicalGroup(1, [ff])
        airfoil = gmsh.model.addPhysicalGroup(1, [af])
        gmsh.model.setPhysicalName(1, airfoil, 'airfoil')
        gmsh.model.setPhysicalName(1, farfield, 'farfield')
        gmsh.model.mesh.generate(2)
        gmsh.model.setCurrent(tmp)
    
    def write(self, save_file):
        tmp = gmsh.model.get_current()
        gmsh.model.set_current(self.name)
        gmsh.write(save_file)
        gmsh.model.set_current(tmp)
    

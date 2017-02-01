"""Define `Group`s with parallel topologies for testing"""

from __future__ import division, print_function

from openmdao.core.group import Group
from openmdao.core.indepvarcomp import IndepVarComp
from openmdao.components.exec_comp import ExecComp


class FanOut(Group):
    """Topology where one comp broadcasts an output to two target
    components."""

    def __init__(self):
        super(FanOut, self).__init__()

        self.add_subsystem('p', IndepVarComp('x', 1.0))
        self.add_subsystem('comp1', ExecComp(['y=3.0*x']))
        self.add_subsystem('comp2', ExecComp(['y=-2.0*x']))
        self.add_subsystem('comp3', ExecComp(['y=5.0*x']))

        self.connect("comp1.y", "comp2.x")
        self.connect("comp1.y", "comp3.x")
        self.connect("p.x", "comp1.x")


class FanOutGrouped(Group):
    """Topology where one component broadcasts an output to two target
    components."""

    def __init__(self):
        super(FanOutGrouped, self).__init__()

        self.add_subsystem('iv', IndepVarComp('x', 1.0))
        self.add_subsystem('c1', ExecComp(['y=3.0*x']))

        self.sub = self.add_subsystem('sub', Group())  # ParallelGroup
        self.sub.add_subsystem('c2', ExecComp(['y=-2.0*x']))
        self.sub.add_subsystem('c3', ExecComp(['y=5.0*x']))

        self.add_subsystem('c2', ExecComp(['y=x']))
        self.add_subsystem('c3', ExecComp(['y=x']))

        self.connect('iv.x', 'c1.x')

        self.connect('c1.y', 'sub.c2.x')
        self.connect('c1.y', 'sub.c3.x')

        self.connect('sub.c2.y', 'c2.x')
        self.connect('sub.c3.y', 'c3.x')


class FanIn(Group):
    """Topology where two comps feed a single comp."""

    def __init__(self):
        super(FanIn, self).__init__()

        self.add_subsystem('p1', IndepVarComp('x1', 1.0))
        self.add_subsystem('p2', IndepVarComp('x2', 1.0))
        self.add_subsystem('comp1', ExecComp(['y=-2.0*x']))
        self.add_subsystem('comp2', ExecComp(['y=5.0*x']))
        self.add_subsystem('comp3', ExecComp(['y=3.0*x1+7.0*x2']))

        self.connect("comp1.y", "comp3.x1")
        self.connect("comp2.y", "comp3.x2")
        self.connect("p1.x1", "comp1.x")
        self.connect("p2.x2", "comp2.x")


class FanInGrouped(Group):
    """Topology where two components in a Group feed a single component
    outside of that Group.
    """

    def __init__(self):
        super(FanInGrouped, self).__init__()

        self.add_subsystem('iv', IndepVarComp([
            ('x1', 1.0), ('x2', 1.0)
        ]))

        self.sub = self.add_subsystem('sub', Group())  # ParallelGroup
        self.sub.add_subsystem('c1', ExecComp(['y=-2.0*x']))
        self.sub.add_subsystem('c2', ExecComp(['y=5.0*x']))

        self.add_subsystem('c3', ExecComp(['y=3.0*x1+7.0*x2']))

        self.connect("sub.c1.y", "c3.x1")
        self.connect("sub.c2.y", "c3.x2")

        self.connect("iv.x1", "sub.c1.x")
        self.connect("iv.x2", "sub.c2.x")


class DiamondFlat(Group):
    """Topology: one - two - one.

    This one is flat."""

    def __init__(self):
        super(DiamondFlat, self).__init__()

        self.add_subsystem('iv', IndepVarComp('x', 2.0))

        self.add_subsystem('c1', ExecComp([
            'y1 = 2.0*x1**2',
            'y2 = 3.0*x1'
        ]))

        self.add_subsystem('c2', ExecComp('y1 = 0.5*x1'))
        self.add_subsystem('c3', ExecComp('y1 = 3.5*x1'))

        self.add_subsystem('c4', ExecComp([
            'y1 = x1 + 2.0*x2',
            'y2 = 3.0*x1 - 5.0*x2'
        ]))

        # make connections
        self.connect('iv.x', 'c1.x1')
        self.connect('c1.y1', 'c2.x1')
        self.connect('c1.y2', 'c3.x1')
        self.connect('c2.y1', 'c4.x1')
        self.connect('c3.y1', 'c4.x2')


class Diamond(Group):
    """Topology: one - two - one."""

    def __init__(self):
        super(Diamond, self).__init__()

        self.add_subsystem('iv', IndepVarComp('x', 2.0))

        self.add_subsystem('c1', ExecComp([
            'y1 = 2.0*x1**2',
            'y2 = 3.0*x1'
        ]))

        sub = self.add_subsystem('sub', Group())  # ParallelGroup
        sub.add_subsystem('c2', ExecComp('y1 = 0.5*x1'))
        sub.add_subsystem('c3', ExecComp('y1 = 3.5*x1'))

        self.add_subsystem('c4', ExecComp([
            'y1 = x1 + 2.0*x2',
            'y2 = 3.0*x1 - 5.0*x2'
        ]))

        # make connections
        self.connect('iv.x', 'c1.x1')

        self.connect('c1.y1', 'sub.c2.x1')
        self.connect('c1.y2', 'sub.c3.x1')

        self.connect('sub.c2.y1', 'c4.x1')
        self.connect('sub.c3.y1', 'c4.x2')


class ConvergeDivergeFlat(Group):
    """Topology one - two - one - two - one. This model was critical in
    testing parallel reverse scatters. Thi version is perfectly flat."""

    def __init__(self):
        super(ConvergeDivergeFlat, self).__init__()

        self.add_subsystem('iv', IndepVarComp('x', 2.0))

        self.add_subsystem('c1', ExecComp([
            'y1 = 2.0*x1**2',
            'y2 = 3.0*x1'
        ]))

        self.add_subsystem('c2', ExecComp('y1 = 0.5*x1'))
        self.add_subsystem('c3', ExecComp('y1 = 3.5*x1'))

        self.add_subsystem('c4', ExecComp([
            'y1 = x1 + 2.0*x2',
            'y2 = 3.0*x1 - 5.0*x2'
        ]))

        self.add_subsystem('c5', ExecComp('y1 = 0.8*x1'))
        self.add_subsystem('c6', ExecComp('y1 = 0.5*x1'))
        self.add_subsystem('c7', ExecComp('y1 = x1 + 3.0*x2'))

        # make connections
        self.connect('iv.x', 'c1.x1')

        self.connect('c1.y1', 'c2.x1')
        self.connect('c1.y2', 'c3.x1')

        self.connect('c2.y1', 'c4.x1')
        self.connect('c3.y1', 'c4.x2')

        self.connect('c4.y1', 'c5.x1')
        self.connect('c4.y2', 'c6.x1')

        self.connect('c5.y1', 'c7.x1')
        self.connect('c6.y1', 'c7.x2')


class ConvergeDiverge(Group):
    """Topology: one - two - one - two - one.

    Used for testing parallel reverse scatters.
    """

    def __init__(self):
        super(ConvergeDiverge, self).__init__()

        self.add_subsystem('iv', IndepVarComp('x', 2.0))

        self.add_subsystem('c1', ExecComp([
            'y1 = 2.0*x1**2',
            'y2 = 3.0*x1'
        ]))

        g1 = self.add_subsystem('g1', Group())  # ParallelGroup
        g1.add_subsystem('c2', ExecComp('y1 = 0.5*x1'))
        g1.add_subsystem('c3', ExecComp('y1 = 3.5*x1'))

        self.add_subsystem('c4', ExecComp([
            'y1 = x1 + 2.0*x2',
            'y2 = 3.0*x1 - 5.0*x2'
        ]))

        g2 = self.add_subsystem('g2', Group())  # ParallelGroup
        g2.add_subsystem('c5', ExecComp('y1 = 0.8*x1'))
        g2.add_subsystem('c6', ExecComp('y1 = 0.5*x1'))

        self.add_subsystem('c7', ExecComp('y1 = x1 + 3.0*x2'))

        # make connections
        self.connect('iv.x', 'c1.x1')

        self.connect('c1.y1', 'g1.c2.x1')
        self.connect('c1.y2', 'g1.c3.x1')

        self.connect('g1.c2.y1', 'c4.x1')
        self.connect('g1.c3.y1', 'c4.x2')

        self.connect('c4.y1', 'g2.c5.x1')
        self.connect('c4.y2', 'g2.c6.x1')

        self.connect('g2.c5.y1', 'c7.x1')
        self.connect('g2.c6.y1', 'c7.x2')


class ConvergeDivergeGroups(Group):
    """Topology: one - two - one - two - one.

    Used for testing parallel reverse scatters. This version contains some
    deeper nesting.
    """

    def __init__(self):
        super(ConvergeDivergeGroups, self).__init__()

        self.add_subsystem('iv', IndepVarComp('x', 2.0))

        g1 = self.add_subsystem('g1', Group())  # ParallelGroup
        g1.add_subsystem('c1', ExecComp([
            'y1 = 2.0*x1**2',
            'y2 = 3.0*x1'
        ]))

        g2 = g1.add_subsystem('g2', Group())  # ParallelGroup
        g2.add_subsystem('c2', ExecComp('y1 = 0.5*x1'))
        g2.add_subsystem('c3', ExecComp('y1 = 3.5*x1'))

        g1.add_subsystem('c4', ExecComp([
            'y1 = x1 + 2.0*x2',
            'y2 = 3.0*x1 - 5.0*x2'
        ]))

        g3 = self.add_subsystem('g3', Group())  # ParallelGroup
        g3.add_subsystem('c5', ExecComp('y1 = 0.8*x1'))
        g3.add_subsystem('c6', ExecComp('y1 = 0.5*x1'))

        self.add_subsystem('c7', ExecComp('y1 = x1 + 3.0*x2'))

        # make connections
        self.connect('iv.x', 'g1.c1.x1')

        g1.connect('c1.y1', 'g2.c2.x1')
        g1.connect('c1.y2', 'g2.c3.x1')

        self.connect('g1.g2.c2.y1', 'g1.c4.x1')
        self.connect('g1.g2.c3.y1', 'g1.c4.x2')

        self.connect('g1.c4.y1', 'g3.c5.x1')
        self.connect('g1.c4.y2', 'g3.c6.x1')

        self.connect('g3.c5.y1', 'c7.x1')
        self.connect('g3.c6.y1', 'c7.x2')
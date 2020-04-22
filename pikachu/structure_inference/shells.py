from pikachu.structure_inference.electron import Electron
from pikachu.structure_inference.atom import ATOM_PROPERTIES


class Shell:
    
    def __init__(self, atom, shell_nr):
        self.shell_nr = shell_nr
        self.orbital_sets = {}
        self.orbitals = {}
        self.bonding_orbitals = []
        self.atom = atom

        
        self.define_orbitals()
        self.find_bonding_orbitals()

    def define_orbitals(self):
        self.orbitals = {}
        self.orbital_sets[f'{self.shell_nr}s'] = OrbitalSet(self.atom, self.shell_nr, 's')
        if self.shell_nr >= 2:
            self.orbital_sets[f'{self.shell_nr}p'] = OrbitalSet(self.atom, self.shell_nr, 'p')
        if self.shell_nr >= 3:
            self.orbital_sets[f'{self.shell_nr}d'] = OrbitalSet(self.atom, self.shell_nr, 'd')
        if self.shell_nr >= 4:
            self.orbital_sets[f'{self.shell_nr}f'] = OrbitalSet(self.atom, self.shell_nr, 'f')

        for orbital_set in self.orbital_sets:
            for orbital in self.orbital_sets[orbital_set].orbitals:
                self.orbitals[orbital.__hash__()] = orbital

    def __hash__(self):
        return f'{self.atom.nr}_{self.shell_nr}'

    def __repr__(self):
        return f'{self.atom.nr}_{self.shell_nr}'

    def hybridise(self, hybridisation):
        if hybridisation == 'sp3':
            self.sp_hybridise(3)
        elif hybridisation == 'sp2':
            self.sp_hybridise(2)
        elif hybridisation == 'sp':
            self.sp_hybridise(1)
        elif hybridisation == 'sp3d':
            self.spd_hybridise(1)
        elif hybridisation == 'sp3d2':
            self.spd_hybridise(2)

        for orbital_name in self.orbitals:
            orbital = self.orbitals[orbital_name]
            for electron in orbital.electrons:
                if self.atom == electron.atom:
                    electron.set_orbital(orbital)

    def dehybridise(self):
        for orbital_set in self.orbital_sets:
            for i, orbital in enumerate(self.orbital_sets[orbital_set].orbitals):
                if orbital.orbital_type not in {'s', 'p', 'd', 'f'}:
                    new_orbital_type = self.orbital_sets[orbital_set].orbital_type
                    if new_orbital_type != 's':
                        new_orbital_nr = i + 1
                    else:
                        new_orbital_nr = None

                    orbital.orbital_type = new_orbital_type
                    orbital.orbital_nr = new_orbital_nr

        for orbital_name in self.orbitals:
            orbital = self.orbitals[orbital_name]
            for electron in orbital.electrons:
                if self.atom == electron.atom:
                    electron.set_orbital(orbital)


    def sp_hybridise(self, p_nr):
        #print("P nr:", p_nr, self.atom)
        hybridised_p = 0

        orbital_nr = 1
        
        for orbital_name in self.orbitals:
            orbital = self.orbitals[orbital_name]
            if orbital.orbital_type == 's':
                orbital.orbital_nr = orbital_nr
                orbital.orbital_type = f'sp{p_nr}'
                orbital_nr += 1
            elif orbital.orbital_type == 'p':
                if not orbital.bond or orbital.bonding_orbital == 'sigma':
                    if hybridised_p < p_nr:
                        orbital.orbital_type = f'sp{p_nr}'
                        orbital.orbital_nr = orbital_nr
                        hybridised_p += 1
                        orbital_nr += 1
            

                        
    def spd_hybridise(self, d_nr):
        hybridised_d = 0

        orbital_nr = 1

        for orbital_name in self.orbitals:
            orbital = self.orbitals[orbital_name]
            if orbital.orbital_type == 's':
                orbital.orbital_type = f'sp3d{d_nr}'
                orbital.orbital_nr = orbital_nr
                orbital_nr += 1
            if orbital.orbital_type == 'p':
                orbital.orbital_type = f'sp3d{d_nr}'
                orbital.orbital_nr = orbital_nr
                orbital_nr += 1
            elif orbital.orbital_type == 'd':
                if not orbital.bond or orbital.bonding_orbital == 'sigma':
                    if hybridised_d < d_nr:
                        orbital.orbital_type = f'sp3d{d_nr}'
                        hybridised_d += 1
                        orbital.orbital_nr = orbital_nr
                        orbital_nr += 1

    def excite(self):
        assert self.is_excitable()
        electron_nr = self.count_electrons()
        
        for orbital_set in ATOM_PROPERTIES.orbital_order:
            if orbital_set in self.orbital_sets:
                for orbital in self.orbital_sets[orbital_set].orbitals:
                    for i in range(orbital.electron_nr):
                        orbital.empty_orbital()
                    
                    if electron_nr > 0:
                        orbital.fill_orbital()
                        electron_nr -= 1
                
                        
    def get_lone_pair_nr(self):
        lone_pair_nr = 0
        for orbital_name in self.orbitals:
            orbital = self.orbitals[orbital_name]
            if orbital.electron_nr == 2:
                if orbital.electrons[0].atom == orbital.electrons[1].atom:
                    lone_pair_nr += 1
        return lone_pair_nr

    def get_lone_electrons(self):
        lone_electrons = 0
        for orbital_name in self.orbitals:
            orbital = self.orbitals[orbital_name]
            if orbital.electron_nr == 1:
                lone_electrons += 1

        return lone_electrons

    def find_bonding_orbitals(self):
        self.bonding_orbitals = []
        
        for orbital in self.orbitals:
            if self.orbitals[orbital].electron_nr == 1:
                self.bonding_orbitals.append(orbital)
                
    def count_electrons(self):
        electron_nr = 0
        for orbital_name in self.orbitals:
            orbital = self.orbitals[orbital_name]
            electron_nr += orbital.electron_nr

        return electron_nr

    def count_orbitals(self):
        orbital_nr = len(list(self.orbitals.keys()))

        return orbital_nr
        

    def is_excitable(self):
        electron_nr = self.count_electrons()
        orbital_nr = self.count_orbitals()
        if orbital_nr >= electron_nr:
            return True
        else:
            return False

    def drop_electrons(self):

        
        lone_orbitals = []

        for orbital_set in ATOM_PROPERTIES.orbital_order:
            if orbital_set in self.orbital_sets:
                for orbital in self.orbital_sets[orbital_set].orbitals:
                    if orbital.electron_nr == 1:
                        if not orbital.electrons[0].aromatic:
                            lone_orbitals.append(orbital)


        while len(lone_orbitals) > 1 and lone_orbitals[0].orbital_type != lone_orbitals[-1].orbital_type:
            receiver_orbital = lone_orbitals[0]
            donor_orbital = lone_orbitals[-1]

            moved_electron = donor_orbital.electrons[0]

            donor_orbital.remove_electron(moved_electron)
            receiver_orbital.add_electron(moved_electron)
            receiver_orbital.electrons[1].set_orbital(receiver_orbital)
            

            del lone_orbitals[0]
            del lone_orbitals[-1]

    def print_shell(self):
        for orbital in self.orbitals:
            print(self.orbitals[orbital])

class OrbitalSet:
    def __init__(self, atom, shell_nr, orbital_type):
        self.atom = atom
        self.shell_nr = shell_nr
        
        self.orbital_type = orbital_type
        self.orbitals = []
        self.define_orbitals()
        self.capacity = len(self.orbitals) * 2
        

    def __repr__(self):
        return f'{self.shell_nr}{orbital_type}'


    def define_orbitals(self):
        if self.orbital_type == 's':
            self.append_s_orbital()
        if self.orbital_type == 'p':
            self.append_p_orbitals()
        if self.orbital_type == 'd':
            self.append_d_orbitals()
        if self.orbital_type == 'f':
            self.append_f_orbitals()
        
    def append_s_orbital(self):
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 's'))
    
    def append_p_orbitals(self):
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'p', 1))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'p', 2))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'p', 3))

    def append_d_orbitals(self):
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'd', 1))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'd', 2))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'd', 3))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'd', 4))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'd', 5))
            
    def append_f_orbitals(self):
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'f', 1))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'f', 2))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'f', 3))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'f', 4))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'f', 5))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'f', 6))
        self.orbitals.append(Orbital(self.atom, self.shell_nr, 'f', 7))

    def fill_orbitals(self, electrons):
        while electrons > 0:
            for orbital in self.orbitals:
                if electrons > 0:
                    orbital.fill_orbital()
                    electrons -= 1
                else:
                    break

class Orbital():
    subtype_dict = {'p': {1: 'x',
                          2: 'y',
                          3: 'z'},
                    'd': {1: 'z^2',
                          2: 'zx',
                          3: 'yz',
                          4: 'xy',
                          5: 'x^2-y^2'},
                    'f': {1: 'z^3-3/5zr^2',
                          2: 'x^3-3/5xr^2',
                          3: 'y^3-3/5yr^2',
                          4: 'xyz',
                          5: 'y(x^2-z^2)',
                          6: 'x(z^2-y^2)',
                          7: 'z(x^2-y^2)'}
                    }
    
    def __init__(self, atom, shell_nr, orbital_type, orbital_nr = None):
        self.shell_nr = shell_nr
        self.orbital_type = orbital_type
        self.orbital_nr = orbital_nr
        self.electron_nr = 0
        self.electrons = []
        self.atom = atom
        self.bond = None
        self.bonding_orbital = None


    def __hash__(self):
        if self.orbital_nr:                               
                                        
            return f'{self.shell_nr}{self.orbital_type}{self.orbital_nr}'
        
        else:
            return f'{self.shell_nr}{self.orbital_type}'

    def __repr__(self):
        if self.orbital_nr:                               
                                        
            return f'{self.shell_nr}{self.orbital_type}{self.orbital_nr}'
        
        else:
            return f'{self.shell_nr}{self.orbital_type}'

    def set_electron_nr(self):
        self.electron_nr = len(self.electrons)

    def set_bond(self, bond, bonding_orbital):
        self.bond = bond
        self.bonding_orbital = bonding_orbital

    def remove_bond(self):
        self.bond = None
        self.bonding_orbital = None

    def fill_orbital(self):
        """
        """
        assert self.electron_nr < 2

        self.electrons.append(Electron(self.shell_nr, self.orbital_type,
                                       self.orbital_nr, 0.5, self.atom))
        self.set_electron_nr()
        
        if self.electron_nr == 2:
            self.electrons[0].pair(self.electrons[1])

    def empty_orbital(self):
        """
        """
        assert self.electron_nr > 0
        
        del self.electrons[-1]
        self.set_electron_nr()

        if self.electron_nr == 1:
            self.electrons[0].unpair()
            
        
    def add_electron(self, electron):
        assert self.electron_nr < 2

        self.electrons.append(electron)
        self.set_electron_nr()
        

        if self.electron_nr == 2:
            self.electrons[0].pair(self.electrons[1])
            

    def remove_electron(self, electron):
        assert electron in self.electrons
        
        self.electrons.remove(electron)
        self.set_electron_nr()

        if self.electron_nr == 1:

            self.electrons[0].unpair()

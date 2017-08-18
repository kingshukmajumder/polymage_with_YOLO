# from ctypes import cdll, Structure, c_int, c_double, c_uint
from cffi import FFI
import islpy as isl

TAG = "libpluto"
_pluto_header_str = \
"""

    struct plutoMatrix {
        /* The values */
        long long int **val;

        int nrows;
        int ncols;

        /* Pre-allocated number of rows */
        int alloc_nrows;
        int alloc_ncols;
    };
    typedef struct plutoMatrix PlutoMatrix;


    struct plutoOptions{

        /* To tile or not? */
        int tile;

        /* Intra-tile optimization */
        int intratileopt;

        /* Load-balanced tiling */
        int lbtile;

        /* Load-balanced tiling (one dimensional concurrent start)*/
        int partlbtile;

        /* Extract scop information from libpet*/
        int pet;

        /* dynamic scheduling
         * using Synthesized Runtime Interface */
        int dynschedule;

        /* dynamic scheduling - previous technique of
         * building the entire task graph in memory
         * using Intel TBB Flow Graph scheduler */
        int dynschedule_graph;

        /* dynamic scheduling - previous technique of
         * building the entire task graph in memory
         * using a custom DAG scheduler */
        // no longer maintained
        int dynschedule_graph_old;

        /* consider transitive dependences between tasks */
        int dyn_trans_deps_tasks;

        /* parallelization */
        int parallel;

        /* prefer pure inner parallelism to pipelined parallelism */
        int innerpar;

        /* Automatic unroll/unroll-jamming of loops */
        int unroll;

        /* unroll/jam factor */
        int ufactor;

        /* Enable or disable post-transformations to make code amenable to
         * vectorization (default - enabled) */
        int prevector;

        /* consider RAR dependences */
        int rar;

        /* Decides the fusion algorithm (MAXIMAL_FUSE, NO_FUSE, or SMART_FUSE) */
        int fuse;

        /* for debugging - print default cloog-style total */
        int scancount;

        /* parameters will be assumed to be at least this much */
        /* This is appended to the context passed to cloog */
        int codegen_context;

        /* Loop depth (1-indexed) to force as parallel */
        int forceparallel;

        /* multiple (currently two) degrees of pipelined parallelism */
        int multipar;

        /* Tile for L2 too */
        /* By default, only L1 tiling is done; under parallel execution, every
         * processor executes a sequence of L1 tiles (OpenMP adds another blocking
         * on the parallel loop). With L2 tiling, each processor executes a
         * sequence of L2 tiles and barrier is done after a group of L2 tiles is
         * exectuted -- causes load imbalance due to pipe startup when problem
         * sizes are not huge */
        int l2tile;


        /* NOTE: --ft and --lt are to manually force tiling depths */
        /* First depth to tile (starting from 0) */
        int ft;
        /* Last depth to tile (indexed from 0)  */
        int lt;

        /* Output for debugging */
        int debug;

        /* More debugging output */
        int moredebug;

        /* Not implemented yet: Don't output anything unless something fails */
        int quiet;

        /* Pure polyhedral unrolling (instead of postpass) */
        int polyunroll;

        /* Identity transformation */
        int identity;

        /* Identity transformation */
        int identity_data_dist;

        /* Generate scheduling pragmas for Bee+Cl@k */
        int bee;

        /* Force this for cloog's -f */
        int cloogf;

        /* Force this for cloog's -l */
        int cloogl;

        /* Enable cloog's -sh (simple convex hull) */
        int cloogsh;

        /* Enable cloog's -backtrack */
        int cloogbacktrack;

        /* Use isl to compute dependences (default) */
        int isldep;

        /* Use candl to compute dependences */
        int candldep;

        /* Access-wise dependences with ISL */
        int isldepaccesswise;

        /* Coalesce ISL deps */
        int isldepcoalesce;

        /* Compute lastwriter for dependences */
        int lastwriter;

        /* DEV: Don't use cost function */
        int nodepbound;

        /* hard upper bound for transformation coefficients */
        int coeff_bound;

        /* Ask candl to privatize */
        int scalpriv;

        /* No output from Pluto if everything goes right */
        int silent;

        /* Read input from a .scop file */
        int readscop;

        /* Use PIP as ilp solver. */
        int pipsolve;

        /* Use isl as ilp solver. */
        int islsolve;

        int glpksolve;

        /* Index set splitting */
        int iss;

        int distmem;

        /*  adding support to generate opencl code */
        int opencl;

        /* use multi-level distribution function */
        /* for dynamic scheduling or distributed-memory code */
        /* OFF by default */
        int multi_level_distribution;

        int commopt;

        /*Communication code generation using flow-out partitioning */
        int commopt_fop;
        /* generate code to choose between unicast pack and multicast pack
         * for each partition at runtime */
        int fop_unicast_runtime;

        /*Communication code generation using flow-out intersection flow-in */
        int commopt_foifi;

        /*Report communication for distributed memory*/
        int timereport;

        /* if true, variables are not declared globally
         * but each variable's declaration is provided
         * through the macro '#define __DECLARATION_OF_<variable-name> <declaration>'*/
        int variables_not_global;

        int data_dist;
        int verify_output;

        int mpiomp;
        int fusesends;
        int blockcyclic;
        int cyclesize;

        //enables mod eliminate and data ptr optimization for data tiling
        int data_tile_opt;

        //Propagates the bounding box constraints across non fused loops
        int global_opt;

        //auto compute pi
        int compute_pi;

        //max number of tiles to be used while computing pi
        int num_tiles_per_dim;

        //number of initial partitions used while computing pi
        int num_inital_partitions;

        /* Output file name supplied from -o */
        char *out_file;

        /* Polyhedral compile time stats */
        int time;

        /* Experimental optimizations to make Pluto faster/scalable */
        int fast;

        /* Eliminate Farkas multipliers using PolyLib */
        int efup;

        /* fast linear independence check */
        int flic;

        /* SCoP number when processing multiple SCoPs per file */
        int scopnum;
    };
    typedef struct plutoOptions PlutoOptions;



    struct remapping {
        int nstmts;
        PlutoMatrix **stmt_inv_matrices;
        int **stmt_divs;
    };
    typedef struct remapping Remapping;

    PlutoOptions *pluto_options_alloc();
    void pluto_options_free(PlutoOptions *);


    void pluto_schedule_str(const char *domains_str,
        const char *dependences_str,
        char** schedules_str_buffer_ptr,
        char** p_loops,
        PlutoOptions *options);

    void pluto_schedules_strbuf_free(char *schedules_str_buffer);


   // Remapping *pluto_get_remapping_str(const char *domains_str,
   //     const char *dependences_str,
   //     char** schedules_str_buffer_ptr,
   //    PlutoOptions *options);


    void pluto_get_remapping_str(const char *domains_str,
            const char *dependences_str,
            Remapping **remapping_ptr,
            PlutoOptions *options);
"""



class Remapping(object):
    def __init__(self, pluto_ffi, raw_ptr):
        self._pluto_ffi = pluto_ffi
        self._raw_ptr = raw_ptr

        self._nstmts = self._raw_ptr.nstmts

        self._stmt_divs = []
        self._inv_matrices = []

        for i in range(self._raw_ptr.nstmts):
            inv_matrix = self._raw_ptr.stmt_inv_matrices[i]
            stmt_div = self._raw_ptr.stmt_divs[i]

            nrows = inv_matrix.nrows
            ncols = inv_matrix.ncols

            inv_matrix = [[inv_matrix.val[r][c] for c in range(ncols)]
                        for r in range(nrows)]
            self._inv_matrices.append(inv_matrix)

            stmt_div = [stmt_div[r] for r in range(nrows)]
            self._stmt_divs.append(stmt_div)

    @property
    def inv_matrices(self):
        """
        Returns the inverse matrix corresponding to a transformation.
        The matrix is the affine transform that takes points in the
        range to the points in the domain
        """
        return self._inv_matrices

    @property
    def divs(self):
        """
        Returns the common demnomiator of all elements per row.
        length of divs = #rows of inv_matrix
        """
        return self._stmt_divs

    @property
    def nstmts(self):
        return self._nstmts

    def __str__(self):
        import numpy as np
        str = ""
        for i in range(self.nstmts):
            matrix = self._inv_matrices[i]
            div = self._stmt_divs[i]
            str +=  "inverse matrix:\n%s \n\n div:\n%s" % (np.array(matrix),
                    np.array(div))
            str += "\n===\n"
        return str

class PlutoOptions(object):
    """
    Options to be passed to PLUTO during schedules creation

    TODO: add more PLUTO options as desired
    """
    def __init__(self, pluto_ffi, raw_options_ptr):
        self._pluto_ffi = pluto_ffi
        self._raw_ptr = raw_options_ptr
        self._raw_ptr.parallel = 1
        self._raw_ptr.partlbtile = 1
        self._raw_ptr.lbtile = 1
        self._raw_ptr.tile = 1
        self._raw_ptr.intratileopt = 0
        self._raw_ptr.debug = self._raw_ptr.moredebug = 0

    @property
    def partlbtile(self):
        """
        Load-balanced tiling (one dimensional concurrent start)
        """
        return self._raw_ptr.partlbtile

    @partlbtile.setter
    def partlbtile(self, partlbtile):
        """
        Set load-balanced tiling (one dimensional concurrent start) status

        Parameters
        ----------
        partlbtile : Bool
        """
        return
        # self._raw_ptr.partlbtile = 1 if partlbtile else 0

    def __del__(self):
        self._pluto_ffi._destroy_raw_options_ptr(self._raw_ptr)


class LibPluto(object):
    """
    Represents the FFI to libpluto. On construction, this loads
    libpluto.so and maintains a reference to it as long as it lives
    """
    def __init__(self):
        self.ffi = FFI()

        self.ffi.cdef(_pluto_header_str)
        self.so = self.ffi.dlopen('libpluto.so')

        #print('Loaded lib {0}'.format(self.so))

    def create_options(self):
        """
        Creates a PlutoOptions object, which allows configuring PLUTO.

        Parameters
        ----------
        None

        Returns
        -------
        PlutoOptions to configure
        """
        return PlutoOptions(self, self.so.pluto_options_alloc())

    def _destroy_raw_remapping_ptr(self, raw_ptr):
        pass

    def _destroy_raw_options_ptr(self, raw_options_ptr):
        """
        Frees a raw C PlutoOptions* owned by Python PlutoOptions

        NOTE
        ----
        This function is internal, and should *only* be called by
        PlutoOptions
        """
        # HACK: don't free, try to figure out why there's a segfault
        # self.so.pluto_options_free(raw_options_ptr)

    def schedule(self, ctx, domains, dependences, pluto_options, parallel_loops):

        if isinstance(domains, isl.BasicSet):
            domains = isl.UnionSet.from_basic_set(domains)

        assert isinstance(domains, isl.UnionSet)

        if isinstance(dependences, isl.BasicMap):
            dependences = isl.UnionMap.from_basic_map(dependences)
        assert isinstance(dependences, isl.UnionMap)
        assert isinstance(pluto_options, PlutoOptions)

        #autolog(header("domains") + str(domains), TAG)
        #autolog(header("depdendences") + str(dependences), TAG)

        domains_str = domains.to_str().encode('utf-8')
        dependences_str = dependences.to_str().encode('utf-8')
        schedule_strbuf_ptr = self.ffi.new("char **")
        p_loops_ptr = self.ffi.new("char **")

        self.so.pluto_schedule_str(domains_str, dependences_str,
                                          schedule_strbuf_ptr,
                                          p_loops_ptr,
                                          pluto_options._raw_ptr)

        assert schedule_strbuf_ptr[0] != self.ffi.NULL, \
            ("unable to get schedule from PLUTO")

        schedule_str = self.ffi.string(schedule_strbuf_ptr[0]).decode('utf-8')
        #print("schedule_str = ", schedule_str)

        ploops_str = self.ffi.string(p_loops_ptr[0]).decode('utf-8')
        #print("nploops_str = ", ploops_str)

        # nploops_str would be a csv of list
        ploops_str_list = ploops_str.split(",")

        # TODO: very dangerous - relying on output string to represent int
        # number of parallel loops
        nploops = int(ploops_str_list[0])

        # collect all parallel loop dims in parallel_loops
        for i in range(1, nploops+1):
            parallel_loop = int(ploops_str_list[i])
            #print("Parallel loop:", parallel_loop)
            parallel_loops.append(parallel_loop-1)  # convert to 0-indexing
        #print("parallel_loops = ", parallel_loops)

        schedule = isl.UnionMap.read_from_str(ctx, schedule_str)
        #print("schedule = ", schedule)

        self.so.pluto_schedules_strbuf_free(schedule_strbuf_ptr[0])

        # remapping = self.create_remapping()
        remapping_ptr = self.ffi.new("Remapping **");

        self.so.pluto_get_remapping_str(domains_str, dependences_str,
                remapping_ptr, pluto_options._raw_ptr)

        remapping = Remapping(self, remapping_ptr[0])

        return schedule

    def get_remapping(self, ctx, domains, dependences, pluto_options):
        if isinstance(domains, isl.BasicSet):
            domains = isl.UnionSet.from_basic_set(domains)

        assert isinstance(domains, isl.UnionSet)

        if isinstance(dependences, isl.BasicMap):
            dependences = isl.UnionMap.from_basic_map(dependences)
        assert isinstance(dependences, isl.UnionMap)
        assert isinstance(pluto_options, PlutoOptions)

        #autolog(header("domains") + str(domains), TAG)
        #autolog(header("depdendences") + str(dependences), TAG)

        domains_str = domains.to_str().encode('utf-8')
        dependences_str = dependences.to_str().encode('utf-8')

        remapping_ptr = self.ffi.new("Remapping **");

        self.so.pluto_get_remapping_str(domains_str, dependences_str,
                remapping_ptr, pluto_options._raw_ptr)

        remapping = Remapping(self, remapping_ptr[0])

        return remapping

# This is somewhat of a hack, just to run a "test" if this file is
# executed separately.
# TODO: move this to a separate file
if __name__ == "__main__":
    pluto = LibPluto()

    ctx = isl.Context.alloc()
    pluto_opts = pluto.create_options()
    pluto_opts.partlbtile = 1

    domains = isl.UnionSet.read_from_str(ctx, (
        " [R, T] -> { S_0[i0, i1] : 0 <= i0 <= T and 0 <= i1 <= R - 1; }"))


    deps = isl.UnionMap.read_from_str(ctx,
        ("[R, T] -> {"
        "S_0[i0, i1] -> S_0[i0 + 1, i1 - 1] : 0 <= i0 <= T - 1 and 1 <= i1 <= R - 2; "
        "S_0[i0, i1] -> S_0[i0 + 1, i1 + 1] : 0 <= i0 <= T - 1 and 1 <= i1 <= R - 2; }"))

    sched  = pluto.schedule(ctx, domains, deps, pluto_opts)
    remapping = pluto.get_remapping(ctx, domains, deps, pluto_opts)
    #print("schedule: %s" % sched)
    #print("remapping: %s" % remapping)

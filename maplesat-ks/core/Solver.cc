/***************************************************************************************[Solver.cc]
Copyright (c) 2003-2006, Niklas Een, Niklas Sorensson
Copyright (c) 2007-2010, Niklas Sorensson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
**************************************************************************************************/

#include <math.h>

#include "mtl/Sort.h"
#include "core/Solver.h"
#include "simp/SimpSolver.h"
#include "core/Dimacs.h"
#include "utils/System.h"

#define MAXORDER 39

FILE* exhaustfile = NULL;
FILE* canonicaloutfile = NULL;
FILE* noncanonicaloutfile = NULL;
FILE* permoutfile = NULL;
FILE* shortoutfile = NULL;
#ifdef UNEMBED_SUBGRAPH_CHECK
FILE* guboutfile = NULL;
#endif
long numsols = 0;
long canon = 0;
long noncanon = 0;
long gubcount = 0;
long gubcounts[17] = {};
double canontime = 0;
double noncanontime = 0;
#ifdef PERM_STATS
long canon_np[MAXORDER] = {};
long noncanon_np[MAXORDER] = {};
#endif
long proofsize = 0;
long canonarr[MAXORDER] = {};
long noncanonarr[MAXORDER] = {};
double canontimearr[MAXORDER] = {};
double noncanontimearr[MAXORDER] = {};
double gubtime = 0;

using namespace Minisat;

int N = 0; // Number of edge variables

//=================================================================================================
// Options:


static const char* _cat = "CORE";

#if BRANCHING_HEURISTIC == CHB || BRANCHING_HEURISTIC == LRB
static DoubleOption  opt_step_size         (_cat, "step-size",   "Initial step size",                             0.40,     DoubleRange(0, false, 1, false));
static DoubleOption  opt_step_size_dec     (_cat, "step-size-dec","Step size decrement",                          0.000001, DoubleRange(0, false, 1, false));
static DoubleOption  opt_min_step_size     (_cat, "min-step-size","Minimal step size",                            0.06,     DoubleRange(0, false, 1, false));
#endif
#if BRANCHING_HEURISTIC == VSIDS
static DoubleOption  opt_var_decay         (_cat, "var-decay",   "The variable activity decay factor",            0.95,     DoubleRange(0, false, 1, false));
#endif
#if ! LBD_BASED_CLAUSE_DELETION
static DoubleOption  opt_clause_decay      (_cat, "cla-decay",   "The clause activity decay factor",              0.999,    DoubleRange(0, false, 1, false));
#endif
static DoubleOption  opt_random_var_freq   (_cat, "rnd-freq",    "The frequency with which the decision heuristic tries to choose a random variable", 0, DoubleRange(0, true, 1, true));
static DoubleOption  opt_random_seed       (_cat, "rnd-seed",    "Used by the random variable selection",         91648253, DoubleRange(0, false, HUGE_VAL, false));
static IntOption     opt_ccmin_mode        (_cat, "ccmin-mode",  "Controls conflict clause minimization (0=none, 1=basic, 2=deep)", 2, IntRange(0, 2));
static IntOption     opt_phase_saving      (_cat, "phase-saving", "Controls the level of phase saving (0=none, 1=limited, 2=full)", 2, IntRange(0, 2));
static BoolOption    opt_rnd_init_act      (_cat, "rnd-init",    "Randomize the initial activity", false);
static BoolOption    opt_luby_restart      (_cat, "luby",        "Use the Luby restart sequence", true);
static IntOption     opt_restart_first     (_cat, "rfirst",      "The base restart interval", 100, IntRange(1, INT32_MAX));
static DoubleOption  opt_restart_inc       (_cat, "rinc",        "Restart interval increase factor", 2, DoubleRange(1, false, HUGE_VAL, false));
static DoubleOption  opt_garbage_frac      (_cat, "gc-frac",     "The fraction of wasted memory allowed before a garbage collection is triggered",  0.20, DoubleRange(0, false, HUGE_VAL, false));
#if BRANCHING_HEURISTIC == CHB
static DoubleOption  opt_reward_multiplier (_cat, "reward-multiplier", "Reward multiplier", 0.9, DoubleRange(0, true, 1, true));
#endif
static StringOption  opt_exhaustive(_cat, "exhaustive", "Output for exhaustive search");
static IntOption     opt_keep_blocking     (_cat, "keep-blocking", "Never forget the blocking clauses that are learned during the exhaustive search (0=off, 1=keep clauses after minimization, 2=keep original clauses)", 2, IntRange(0, 2));
static IntOption     opt_max_exhaustive_var (_cat, "max-exhaustive-var", "Only perform exhaustive search over the variables up to and including this variable index (0=use all edge variables in graph)", 0, IntRange(0, INT32_MAX));
//static BoolOption    opt_fixed_card     (_cat, "fixed-card", "Assume a fixed number of true variables in solution and only use negative literals in exhaustive blocking clauses", false);
//static BoolOption    opt_trust_blocking (_cat, "trust-blocking", "Write proof with trusted blocking clauses", false);
static IntOption     opt_order          (_cat, "order", "Number of vertices in the KS system searching for", 0, IntRange(0, MAXORDER));
//static IntOption     opt_start_col      (_cat, "start-col", "Starting column for which to test for canonicity", 2, IntRange(0, MAXORDER));
#ifdef CANON_CHECK_OPTIONS
static IntOption     opt_inc_col        (_cat, "inc-col", "Check for canonicity every inc_col columns", 1, IntRange(1, MAXORDER));
static IntOption     opt_lookahead      (_cat, "lookahead", "Ensure that this many additional columns have been completed before performing canonicity checking", 0, IntRange(0, MAXORDER));
#endif
static IntOption     opt_skip_last      (_cat, "skip-last", "Skip checking the canonicity on the last skip_last columns", 0, IntRange(0, MAXORDER));
static StringOption  opt_canonical_out  (_cat, "canonical-out", "File to output canonical subgraphs found during search");
static StringOption  opt_noncanonical_out  (_cat, "noncanonical-out", "File to output the noncanonical subgraph blocking clauses");
static StringOption  opt_perm_out       (_cat, "perm-out", "File to output the permutations that witness the noncanonicity of the noncanonical blocking clauses");
static StringOption  opt_short_out       (_cat, "short-out", "File to output the short learnt clauses");
static BoolOption    opt_pseudo_test    (_cat, "pseudo-test",  "Use a pseudo-canonicity test that is faster but may incorrectly label matrices as canonical", true);
static BoolOption    opt_minclause      (_cat, "minclause",   "Minimize learned programmatic clause", true);
#ifdef UNEMBED_SUBGRAPH_CHECK
static StringOption  opt_gub_out        (_cat, "unembeddable-out", "File to output unembeddable subgraphs found during search");
static IntOption     opt_check_gub      (_cat, "unembeddable-check", "Number of minimal unembeddable subgraphs to check for", 0, IntRange(0, 17));
#else
#define opt_check_gub 0
#endif
#ifdef OPT_START_GUB
static IntOption     opt_start_gub      (_cat, "unembeddable-check-start", "Starting unembeddable subgraphs to check for", 0, IntRange(0, 17));
#endif
static IntOption     opt_max_conflicts  (_cat, "max-conflicts", "Limit the number of conflicts (0=unlimited)", 0, IntRange(0, INT32_MAX));
static IntOption     opt_max_proof_size (_cat, "max-proof-size", "File size limit (in MiB) of the generated proof (0=unlimited)", 0, IntRange(0, INT32_MAX));

//=================================================================================================
// Constructor/Destructor:


Solver::Solver() :

    // Parameters (user settable):
    //
    verbosity        (0)
#if BRANCHING_HEURISTIC == CHB || BRANCHING_HEURISTIC == LRB
  , step_size        (opt_step_size)
  , step_size_dec    (opt_step_size_dec)
  , min_step_size    (opt_min_step_size)
#endif
#if BRANCHING_HEURISTIC == VSIDS
  , var_decay        (opt_var_decay)
#endif
#if ! LBD_BASED_CLAUSE_DELETION
  , clause_decay     (opt_clause_decay)
#endif
  , random_var_freq  (opt_random_var_freq)
  , random_seed      (opt_random_seed)
  , luby_restart     (opt_luby_restart)
  , ccmin_mode       (opt_ccmin_mode)
  , phase_saving     (opt_phase_saving)
  , rnd_pol          (false)
  , rnd_init_act     (opt_rnd_init_act)
  , garbage_frac     (opt_garbage_frac)
  , restart_first    (opt_restart_first)
  , restart_inc      (opt_restart_inc)

    // Parameters (the rest):
    //
  , learntsize_factor((double)1/(double)3), learntsize_inc(1.1)

    // Parameters (experimental):
    //
  , learntsize_adjust_start_confl (100)
  , learntsize_adjust_inc         (1.5)

    // Statistics: (formerly in 'SolverStats')
    //
  , solves(0), starts(0), decisions(0), rnd_decisions(0), propagations(0), conflicts(0)
  , dec_vars(0), clauses_literals(0), learnts_literals(0), max_literals(0), tot_literals(0)

  , lbd_calls(0)
#if BRANCHING_HEURISTIC == CHB
  , action(0)
  , reward_multiplier(opt_reward_multiplier)
#endif

  , canonicaloutstring (opt_canonical_out)
  , noncanonicaloutstring (opt_noncanonical_out)
  , permoutstring (opt_perm_out)
  , shortoutstring (opt_short_out)
#ifdef UNEMBED_SUBGRAPH_CHECK
  , guboutstring (opt_gub_out)
#endif
  , exhauststring (opt_exhaustive)
  , ok                 (true)
#if ! LBD_BASED_CLAUSE_DELETION
  , cla_inc            (1)
#endif
#if BRANCHING_HEURISTIC == VSIDS
  , var_inc            (1)
#endif
  , watches            (WatcherDeleted(ca))
  , qhead              (0)
  , simpDB_assigns     (-1)
  , simpDB_props       (0)
  , order_heap         (VarOrderLt(activity))
  , progress_estimate  (0)
  , remove_satisfied   (true)

    // Resource constraints:
    //
  , conflict_budget    (-1)
  , propagation_budget (-1)
  , asynch_interrupt   (false)
{
    if(exhauststring != NULL)
    {   //if(opt_order == 0)
        //    printf("Need to provide order when using exhaustive search\n"), exit(1);
        exhaustfile = fopen(exhauststring, "w");
        opt_exhaustive = NULL;
        use_callback = true;
    }
    if(opt_check_gub > 0)
    {   if(opt_order == 0)
            printf("Need to provide order when using unembeddable checking\n"), exit(1);
        use_callback = true;
    }
    if(opt_order > 0)
    {   n = opt_order;
        N = n*(n-1)/2;
        opt_order = 0;
        use_callback = true;
        if(canonicaloutstring != NULL) {
            canonicaloutfile = fopen(canonicaloutstring, "w");
        }
        if(noncanonicaloutstring != NULL) {
            noncanonicaloutfile = fopen(noncanonicaloutstring, "w");
        }
        if(permoutstring != NULL) {
            permoutfile = fopen(permoutstring, "w");
        }
        if(shortoutstring != NULL) {
            shortoutfile = fopen(shortoutstring, "w");
        }
#ifdef UNEMBED_SUBGRAPH_CHECK
        if(guboutstring != NULL) {
            guboutfile = fopen(guboutstring, "w");
        }
#endif
    }
}


Solver::~Solver()
{
    if(exhaustfile != NULL)
    {   fclose(exhaustfile);
        exhaustfile = NULL;
    }
    if(canonicaloutfile != NULL)
    {   fclose(canonicaloutfile);
        canonicaloutfile = NULL;
    }
    if(noncanonicaloutfile != NULL)
    {   fclose(noncanonicaloutfile);
        noncanonicaloutfile = NULL;
    }
    if(permoutfile != NULL)
    {   fclose(permoutfile);
        permoutfile = NULL;
    }
    if(shortoutfile != NULL)
    {   fclose(shortoutfile);
        shortoutfile = NULL;
    }
#ifdef UNEMBED_SUBGRAPH_CHECK
    if(guboutfile != NULL)
    {   fclose(guboutfile);
        guboutfile = NULL;
    }
#endif
}


//=================================================================================================
// Minor methods:


// Creates a new SAT variable in the solver. If 'decision' is cleared, variable will not be
// used as a decision variable (NOTE! This has effects on the meaning of a SATISFIABLE result).
//
Var Solver::newVar(bool sign, bool dvar)
{
    int v = nVars();
    watches  .init(mkLit(v, false));
    watches  .init(mkLit(v, true ));
    assigns  .push(l_Undef);
    vardata  .push(mkVarData(CRef_Undef, 0));
    //activity .push(0);
    activity .push(rnd_init_act ? drand(random_seed) * 0.00001 : 0);
    seen     .push(0);
    polarity .push(sign);
    decision .push();
    trail    .capacity(v+1);
    lbd_seen.push(0);
    picked.push(0);
    conflicted.push(0);
#if ALMOST_CONFLICT
    almost_conflicted.push(0);
#endif
#if ANTI_EXPLORATION
    canceled.push(0);
#endif
#if BRANCHING_HEURISTIC == CHB
    last_conflict.push(0);
#endif
    total_actual_rewards.push(0);
    total_actual_count.push(0);
    setDecisionVar(v, dvar);
    return v;
}

// Return the number of decimal digits in n + 1 (how variable n is represented in the proof output)
int numdigits(Var n)
{   if(n < 9)
        return 1;
    if(n < 99)
        return 2;
    if(n < 999)
        return 3;
    if(n < 9999)
        return 4;
    if(n < 99999)
        return 5;
    // The loop in this function has been unrolled up to six iterations;
    // the proof size will be off if there are over 10^6 variables
    return 6;
}

// Return the number of bytes used by the given clause in the proof output
int clausestrlen(const vec<Lit>& clause)
{   const int size = clause.size();
    int res = 2+size;
    for(int i=0; i<size; i++)
    {   if(sign(clause[i]))
            res++;
        res += numdigits(var(clause[i]));
    }
    return res;
}

// Return the number of bytes used by the given clause in the proof output
int clausestrlen(const Clause& clause)
{   const int size = clause.size();
    int res = 2+size;
    for(int i=0; i<size; i++)
    {   if(sign(clause[i]))
            res++;
        res += numdigits(var(clause[i]));
    }
    return res;
}

bool Solver::addClause_(vec<Lit>& ps)
{
    assert(decisionLevel() == 0);
    if (!ok) return false;

    // Check if clause is satisfied and remove false/duplicate literals:
    sort(ps);

    vec<Lit>    oc;
    oc.clear();

    Lit p; int i, j, flag = 0;
    for (i = j = 0, p = lit_Undef; i < ps.size(); i++) {
        oc.push(ps[i]);
        if (value(ps[i]) == l_True || ps[i] == ~p || value(ps[i]) == l_False)
          flag = 1;
    }

    for (i = j = 0, p = lit_Undef; i < ps.size(); i++)
        if (value(ps[i]) == l_True || ps[i] == ~p)
            return true;
        else if (value(ps[i]) != l_False && ps[i] != p)
            ps[j++] = p = ps[i];
    ps.shrink(i - j);

    if (flag && (output != NULL)) {
      for (i = j = 0, p = lit_Undef; i < ps.size(); i++)
        fprintf(output, "%i ", (var(ps[i]) + 1) * (-2 * sign(ps[i]) + 1));
      fprintf(output, "0\n");

      fprintf(output, "d ");
      for (i = j = 0, p = lit_Undef; i < oc.size(); i++)
        fprintf(output, "%i ", (var(oc[i]) + 1) * (-2 * sign(oc[i]) + 1));
      fprintf(output, "0\n");
    }

    if(flag) {
      proofsize += clausestrlen(ps);
      proofsize += 2+clausestrlen(oc);
    }

    if (ps.size() == 0)
        return ok = false;
    else if (ps.size() == 1){
        uncheckedEnqueue(ps[0]);
        return ok = (propagate() == CRef_Undef);
    }else{
        CRef cr = ca.alloc(ps, false);
        clauses.push(cr);
        attachClause(cr);
    }

    return true;
}


void Solver::attachClause(CRef cr) {
    const Clause& c = ca[cr];
    assert(c.size() > 1);
    watches[~c[0]].push(Watcher(cr, c[1]));
    watches[~c[1]].push(Watcher(cr, c[0]));
    if (c.learnt()) learnts_literals += c.size();
    else            clauses_literals += c.size(); }


void Solver::detachClause(CRef cr, bool strict) {
    const Clause& c = ca[cr];
    assert(c.size() > 1);
    
    if (strict){
        remove(watches[~c[0]], Watcher(cr, c[1]));
        remove(watches[~c[1]], Watcher(cr, c[0]));
    }else{
        // Lazy detaching: (NOTE! Must clean all watcher lists before garbage collecting this clause)
        watches.smudge(~c[0]);
        watches.smudge(~c[1]);
    }

    if (c.learnt()) learnts_literals -= c.size();
    else            clauses_literals -= c.size(); }


void Solver::removeClause(CRef cr) {
    Clause& c = ca[cr];

    if (output != NULL) {
      fprintf(output, "d ");
      for (int i = 0; i < c.size(); i++)
        fprintf(output, "%i ", (var(c[i]) + 1) * (-2 * sign(c[i]) + 1));
      fprintf(output, "0\n");
    }

    proofsize += 2+clausestrlen(c);

    detachClause(cr);
    // Don't leave pointers to free'd memory!
    if (locked(c)) vardata[var(c[0])].reason = CRef_Undef;
    c.mark(1); 
    ca.free(cr);
}


bool Solver::satisfied(const Clause& c) const {
    for (int i = 0; i < c.size(); i++)
        if (value(c[i]) == l_True)
            return true;
    return false; }


bool colsuntouched[MAXORDER] = {};

// Revert to the state at given level (keeping all assignment at 'level' but not beyond).
//
void Solver::cancelUntil(int level) {
    if (decisionLevel() > level){
        for (int c = trail.size()-1; c >= trail_lim[level]; c--){
            Var      x  = var(trail[c]);
            uint64_t age = conflicts - picked[x];
            if (age > 0) {
                double reward = ((double) conflicted[x]) / ((double) age);
#if BRANCHING_HEURISTIC == LRB
#if ALMOST_CONFLICT
                double adjusted_reward = ((double) (conflicted[x] + almost_conflicted[x])) / ((double) age);
#else
                double adjusted_reward = reward;
#endif
                double old_activity = activity[x];
                activity[x] = step_size * adjusted_reward + ((1 - step_size) * old_activity);
                if (order_heap.inHeap(x)) {
                    if (activity[x] > old_activity)
                        order_heap.decrease(x);
                    else
                        order_heap.increase(x);
                }
#endif
                total_actual_rewards[x] += reward;
                total_actual_count[x] ++;
            }
#if ANTI_EXPLORATION
            canceled[x] = conflicts;
#endif
            assigns [x] = l_Undef;
            if (use_callback && x < N) {
                const int col = 1+(-1+sqrt(1+8*x))/2;
                for(int i=col; i<n; i++)
                    colsuntouched[i] = false;
            }
            if (phase_saving > 1 || (phase_saving == 1) && c > trail_lim.last())
                polarity[x] = sign(trail[c]);
            insertVarOrder(x); }
        qhead = trail_lim[level];
        trail.shrink(trail.size() - trail_lim[level]);
        trail_lim.shrink(trail_lim.size() - level);
    } }


//=================================================================================================
// Major methods:


Lit Solver::pickBranchLit()
{
    Var next = var_Undef;

    // Random decision:
    if (drand(random_seed) < random_var_freq && !order_heap.empty()){
        next = order_heap[irand(random_seed,order_heap.size())];
        if (value(next) == l_Undef && decision[next])
            rnd_decisions++; }

    // Activity based decision:
    while (next == var_Undef || value(next) != l_Undef || !decision[next])
        if (order_heap.empty()){
            next = var_Undef;
            break;
        } else {
#if ANTI_EXPLORATION
            next = order_heap[0];
            uint64_t age = conflicts - canceled[next];
            while (age > 0 && value(next) == l_Undef) {
                double decay = pow(0.95, age);
                activity[next] *= decay;
                if (order_heap.inHeap(next)) {
                    order_heap.increase(next);
                }
                canceled[next] = conflicts;
                next = order_heap[0];
                age = conflicts - canceled[next];
            }
#endif
            next = order_heap.removeMin();
        }

    return next == var_Undef ? lit_Undef : mkLit(next, rnd_pol ? drand(random_seed) < 0.5 : polarity[next]);
}

#define MAX(X,Y) ((X) > (Y)) ? (X) : (Y)
#define MIN(X,Y) ((X) > (Y)) ? (Y) : (X)

// The kth entry estimates the number of permuations needed to show canonicity in order (k+1)
long perm_cutoff[MAXORDER] = {0, 0, 0, 0, 0, 0, 20, 50, 125, 313, 783, 1958, 4895, 12238, 30595, 76488, 191220, 478050, 1195125, 2987813, 7469533, 18673833, 46684583};

// Returns true when the k-vertex subgraph (with adjacency matrix M) is canonical
// M is determined by the current assignment to the first k*(k-1)/2 variables
// If M is noncanonical, then p, x, and y will be updated so that
// * p will be a permutation of the rows of M so that row[i] -> row[p[i]] generates a matrix smaller than M (and therefore demonstrates the noncanonicity of M)
// * (x,y) will be the indices of the first entry in the permutation of M demonstrating that the matrix is indeed lex-smaller than M
// * i will be the maximum defined index defined in p
bool Solver::is_canonical(int k, int p[], int& x, int& y, int& i) {
    int pl[k]; // pl[k] contains the current list of possibilities for kth vertex (encoded bitwise)
    int pn[k+1]; // pn[k] contains the initial list of possibilities for kth vertex (encoded bitwise)
    pl[0] = (1 << k) - 1;
    pn[0] = (1 << k) - 1;
    i = 0;
    int last_x = 0;
    int last_y = 0;

    int np = 1;
    int limit = INT32_MAX;

    // If pseudo-test enabled then stop test if it is taking over 10 times longer than average
    if(opt_pseudo_test && k >= 7) {
        limit = 10*perm_cutoff[k-1];
    }

    while(np < limit) {
        // If no possibilities for ith vertex then backtrack
        if(pl[i]==0) {
            // Backtrack to vertex that has at least two possibilities
            while((pl[i] & (pl[i] - 1)) == 0) {
                if(last_x > p[i]) {
                    last_x = p[i];
                    last_y = 0;
                }
                i--;
                if(i==-1) {
#ifdef PERM_STATS
                    canon_np[k-1] += np;
#endif
                    // No permutations produce a smaller matrix; M is canonical
                    return true;
                }
            }
            // Remove p[i] as a possibility from the ith vertex
            pl[i] = pl[i] & ~(1 << p[i]);
        }

        p[i] = log2(pl[i] & -pl[i]); // Get index of rightmost high bit
        pn[i+1] = pn[i] & ~(1 << p[i]); // List of possibilities for (i+1)th vertex

        // If pseudo-test enabled then stop shortly after the first row is no longer fixed
        if(i == 0 && p[i] == 1 && opt_pseudo_test && k < n) {
            limit = np + 100;
        }

        // Check if the entry on which to begin lex-checking needs to be updated
        if(last_x > p[i]) {
            last_x = p[i];
            last_y = 0;
        }
        if(i == last_x) {
            last_y = 0;
        }

        // Determine if the permuted matrix p(M) is lex-smaller than M
        bool lex_result_unknown = false;
        x = last_x == 0 ? 1 : last_x;
        y = last_y;
        int j;
        for(j=last_x*(last_x-1)/2+last_y; j<k*(k-1)/2; j++) {
            if(x > i) {
                // Unknown if permutation produces a larger or smaller matrix
                lex_result_unknown = true;
                break;
            }
            const int px = MAX(p[x], p[y]);
            const int py = MIN(p[x], p[y]);
            const int pj = px*(px-1)/2 + py;
            if(assigns[j] == l_False && assigns[pj] == l_True) {
                // Permutation produces a larger matrix; stop considering
                break;
            }
            if(assigns[j] == l_True && assigns[pj] == l_False) {
#ifdef PERM_STATS
                noncanon_np[k-1] += np;
#endif
                // Permutation produces a smaller matrix; M is not canonical
                return false;
            }

            y++;
            if(x==y) {
                x++;
                y = 0;
            }
        }
        last_x = x;
        last_y = y;

        if(lex_result_unknown) {
            // Lex result is unknown; need to define p[i] for another i
            i++;
            pl[i] = pn[i];
        }
        else {
            np++;
            // Remove p[i] as a possibility from the ith vertex
            pl[i] = pl[i] & ~(1 << p[i]);
        }
    }

    // Pseudo-test return: Assume matrix is canonical if a noncanonical permutation witness not yet found
#ifdef PERM_STATS
    canon_np[k-1] += np;
#endif
    return true;
}

#ifdef UNEMBED_SUBGRAPH_CHECK
// The 17 minimal unembeddable subgraphs on 10, 11, and 12 vertices
const int gub[17][66] = {
    {1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,1,1}, // I{O_ogI@W (10 vertices, 15 edges) originally ICOedPKL? or It?IQGiDO
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,1,1,1}, // I{d@?gI@w (10 vertices, 16 edges) originally I?qa``eeO or IpD?GUbV?
    {1,1,0,1,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1,0,0,1,0,0,0,0,1,0,1,1,0,0}, // Js`A@GaDGU? (11 vertices, 16 edges) originally J?GX?dH`f_?
    {1,1,1,1,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,1,0,0,1,0,0,0,0,0,1,1,0,1,0,0,0,0,0,1,0,1,0,1,0}, // J{`@?gQBOT? (11 vertices, 17 edges) originally J@`ICC[Gv_?
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,1,1}, // J{dAH?TA_B_ (11 vertices, 18 edges) originally JsOH?`JH_i_
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,1,0,1}, // J{dAH?TA_Q_ (11 vertices, 18 edges) originally J`hSA?hD_F_
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0}, // J{dAH?`DOT? (11 vertices, 18 edges) originally JRPCSGoAgJ_
    {1,1,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,1,0,0,0,0,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1}, // KsP@PGXD?C?B (12 vertices, 17 edges) originally K_GP`GWBACoK
    {1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,1,0,1,0,0,0,0,0,0,1,0,1,0,1,0}, // K{O___IAOL?i (12 vertices, 18 edges) originally Kt?G?DKOoqCo
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,0,1,1,1}, // K{d@?gG@GE?V (12 vertices, 19 edges) originally K_GTAQOP@KbK
    {1,1,1,1,0,0,1,0,0,1,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,1,0,1,0,0,0,0,0,0,1,0,1,0,1,0}, // K{eA@?QAOL?i (12 vertices, 19 edges) originally K@QCAGdA_c~?
    {1,1,1,1,0,0,1,0,0,1,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,0,0,0,1,1}, // K{eA@?RA_I?b (12 vertices, 19 edges) originally KAICH@@DOT^?
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,1,0,1}, // K{d@?gG@oD?L (12 vertices, 19 edges) originally Kko_GC`C?b`q
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,1,1,0,1}, // K{d@?gG@_D_L (12 vertices, 19 edges) originally K`?LAQOP@KbK
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,1,1,0,1,0}, // K{dA@?TA_H_Y (12 vertices, 20 edges) originally K`?KA@se_YCX
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1,0,0,1,1}, // K{dA@?TB?F?R (12 vertices, 20 edges) originally Ks?I@?XDaTCi
    {1,1,1,1,0,0,1,0,0,1,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1,1}  // K{dAH?TC_Q?R (12 vertices, 20 edges) originally KqCaC?[I_J?Z
};

// Returns true when the k-vertex subgraph (with adjacency matrix M) contains the gth minimal unembeddable graph
// M is determined by the current assignment to the first k*(k-1)/2 variables
// If an unembeddable subgraph is found in M, P is set to the mapping from the rows of M to the rows of the lex greatest representation of the unembeddable adjacency matrix (and p is the inverse of P)
bool Solver::has_gub_subgraph(int k, int* P, int* p, int g) {
    //const int gub[45] = {1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1};
    //const int gub_indices[16] = {0, 1, 2, 3, 6, 9, 11, 17, 24, 26, 32, 34, 41, 42, 43, 44};
    //const int gub_indices_y[16] = {0, 0, 1, 0, 0, 3, 1, 2, 3, 5, 4, 6, 5, 6, 7, 8};
    //const int gub_indices_by_col[11] = {0, 0, 1, 3, 4, 6, 7, 8, 10, 12, 16};

    int pl[12]; // pl[k] contains the current list of possibilities for kth vertex (encoded bitwise)
    int pn[13]; // pn[k] contains the initial list of possibilities for kth vertex (encoded bitwise)
    pl[0] = (1 << k) - 1;
    pn[0] = (1 << k) - 1;
    int i = 0;

    while(1) {
        // If no possibilities for ith vertex then backtrack
        if(pl[i]==0) {
            // Backtrack to vertex that has at least two possibilities
            while((pl[i] & (pl[i] - 1)) == 0) {
                i--;
                if(i==-1) {
                    // No permutations produce a matrix containing the gth submatrix
                    return false;
                }
            }
            // Remove p[i] as a possibility from the ith vertex
            pl[i] = pl[i] & ~(1 << p[i]);
        }

        p[i] = log2(pl[i] & -pl[i]); // Get index of rightmost high bit
        pn[i+1] = pn[i] & ~(1 << p[i]); // List of possibilities for (i+1)th vertex

        // Determine if the permuted matrix p(M) is contains the gth submatrix
        bool result_known = false;
        for(int j=0; j<i; j++) {
            if(!gub[g][i*(i-1)/2+j])
                continue;
            const int px = MAX(p[i], p[j]);
            const int py = MIN(p[i], p[j]);
            const int pj = px*(px-1)/2 + py;
            if(assigns[pj] == l_False) {
                // Permutation sends a non-edge to a gth submatrix edge; stop considering
                result_known = true;
                break;
            }
        }

        if(!result_known && ((i == 9 && g < 2) || (i == 10 && g < 7) || i == 11)) {
            // The complete gth submatrix found in p(M)
            for(int j=0; j<=i; j++) {
                P[p[j]] = j;
            }
            return true;
        }
        if(!result_known) {
            // Result is unknown; need to define p[i] for another i
            i++;
            pl[i] = pn[i];
        }
        else {
            // Remove p[i] as a possibility from the ith vertex
            pl[i] = pl[i] & ~(1 << p[i]);
        }
    }
}
#endif

#include <set>

std::set<unsigned long> canonical_hashes[MAXORDER];
std::set<unsigned long> solution_hashes;

#include "hash_values.h"

// A callback function for programmatic interface. If the callback detects conflicts, then
// refine the clause database by adding clauses to out_learnts. This function is called
// very frequently, if the analysis is expensive then add code to skip the analysis on
// most calls. However, if complete is set to true, do not skip the analysis or else the
// solver will be unsound.
//
// complete: true if and only if the current trail is a complete assignment that satisfies
//           the clause database. Note that not every variable is necessarily assigned since
//           the simplification steps may have removed some variables! If complete is true,
//           the solver will return satisfiable immediately unless this function returns at
//           least one clause.
void Solver::callbackFunction(bool complete, vec<vec<Lit> >& out_learnts) {

    if(!use_callback)
        return;

    const int max_exhaust_var = opt_max_exhaustive_var == 0 ? N : opt_max_exhaustive_var;
    long hash = 0;

    // Initialize i to be the first column that has been touched since the last analysis
    int i = 2;
    for(; i < n; i++) {
        if(!colsuntouched[i])
            break;
    }
    // Ensure variables are defined and update current graph hash
    for(int j = 0; j < i*(i-1)/2; j++) {
        if(assigns[j] == l_Undef)
            return;
        else if(assigns[j] == l_True)
            hash += hash_values[j];
    }
    for(; i < n - opt_skip_last; i++) {
        // Ensure variables are defined and update current graph hash
        for(int j = i*(i-1)/2; j < i*(i+1)/2; j++) {
            if(assigns[j]==l_Undef) {
                return;
            }
            if(assigns[j]==l_True) {
                hash += hash_values[j];
            }
        }
        colsuntouched[i] = true;

#ifdef CANON_CHECK_OPTIONS
        // Ensure variables are defined for an additional opt_lookahead columns
        for(int j = i*(i+1)/2; j < (i+opt_lookahead)*(i+opt_lookahead+1)/2 && j < N; j++) {
            if(assigns[j]==l_Undef) {
                return;
            }
        }

        // Only check canonicity every inc_col columns
        if ((n-1)%opt_inc_col != i%opt_inc_col)
            continue;
#endif

        // Check if current graph hash has been seen
        if(canonical_hashes[i].find(hash)==canonical_hashes[i].end())
        {

            // Found a new subgraph of order i+1 to test for canonicity
            const double before = cpuTime();
            // Run canonicity check
            int p[i+1]; // Permutation on i+1 vertices
            int x, y;   // These will be the indices of first adjacency matrix entry that demonstrates noncanonicity (when such indices exist)
            int mi;     // This will be the index of the maximum defined entry of p
            bool ret = (hash == 0) ? true : is_canonical(i+1, p, x, y, mi);
#ifdef VERBOSE
            if(!ret) {
                printf("x: %d y: %d, mi: %d, ", x, y, mi);
                printf("p^(-1)(x): %d, p^(-1)(y): %d | ", p[x], p[y]);
                for(int j=0; j<i+1; j++) {
                    if(j != p[j]) {
                        printf("%d ", p[j]);
                    } else printf("* ");
                }
                printf("\n");
            }
#endif
            const double after = cpuTime();

            // If subgraph is canonical
            if (ret) {
                canon++;
                canontime += (after-before);
                canonarr[i]++;
                canontimearr[i] += (after-before);
                canonical_hashes[i].insert(hash);

                if(canonicaloutfile != NULL) {
                    fprintf(canonicaloutfile, "a ");
                    for(int j = 0; j < i*(i+1)/2; j++)
                        fprintf(canonicaloutfile, "%s%d ", assigns[j]==l_True ? "" : "-", j+1);
                    fprintf(canonicaloutfile, "0\n");
                    fflush(canonicaloutfile);
                }
#ifdef VERBOSE
                int count = 0;
                int A[n][n] = {};
                for(int jj=0; jj<i+1; jj++) {
                    for(int ii=0; ii<jj; ii++) {
                        if(assigns[count]==l_True) {
                            A[ii][jj] = 1;
                            A[jj][ii] = 1;
                        }
                        count++;
                    }
                }
                for(int ii=0; ii<i+1; ii++) {
                    for(int jj=0; jj<i+1; jj++) {
                        printf("%d", A[ii][jj]);
                    }
                    printf("\n");
                }
                printf("\n");
#endif
            }
            // If subgraph is not canonical then block it
            else {
                noncanon++;
                noncanontime += (after-before);
                noncanonarr[i]++;
                noncanontimearr[i] += (after-before);
                out_learnts.push();

                if(opt_minclause) {
                    // Generate a blocking clause smaller than the naive blocking clause
                    out_learnts[0].push(~mkLit(x*(x-1)/2+y));
                    const int px = MAX(p[x], p[y]);
                    const int py = MIN(p[x], p[y]);
                    out_learnts[0].push(mkLit(px*(px-1)/2+py));
                    for(int ii=0; ii < x+1; ii++) {
                        for(int jj=0; jj < ii; jj++) {
                            if(ii==x && jj==y) {
                                break;
                            }
                            const int pii = MAX(p[ii], p[jj]);
                            const int pjj = MIN(p[ii], p[jj]);
                            if(ii==pii && jj==pjj) {
                                continue;
                            } else if(assigns[ii*(ii-1)/2+jj] == l_True) {
                                out_learnts[0].push(~mkLit(ii*(ii-1)/2+jj));
                            } else if (assigns[pii*(pii-1)/2+pjj] == l_False) {
                                out_learnts[0].push(mkLit(pii*(pii-1)/2+pjj));
                            }
                        }
                    }
                }
                else {
                    // Generate the naive blocking clause
                    for(int j = 0; j < i*(i+1)/2; j++)
                        out_learnts[0].push(mkLit(j, assigns[j]==l_True));
                }
                
                if(noncanonicaloutfile != NULL) {
                    //fprintf(noncanonicaloutfile, "a ");
                    for(int j = 0; j < out_learnts[0].size(); j++)
                        fprintf(noncanonicaloutfile, "%s%d ", sign(out_learnts[0][j]) ? "-" : "", var(out_learnts[0][j])+1);
                    fprintf(noncanonicaloutfile, "0\n");
                    fflush(noncanonicaloutfile);
                }

                if(permoutfile != NULL) {
                    for(int j = 0; j <= mi; j++)
                        fprintf(permoutfile, "%s%d", j == 0 ? "" : " ", p[j]);
                    fprintf(permoutfile, "\n");
                }

                // Add the learned clause to the vector of original clauses if the 'keep blocking' option enabled
                if(opt_keep_blocking==2)
                {
                    vec<Lit> clause;
                    out_learnts[0].copyTo(clause);
                    {
                    int max_index = 0;
                    for(int i=1; i<clause.size(); i++)
                        if(level(var(clause[i])) > level(var(clause[max_index])))
                        max_index = i;
                    Lit p = clause[0];
                    clause[0] = clause[max_index];
                    clause[max_index] = p;
                    }

                    {
                    int max_index = 1;
                    for(int i=2; i<clause.size(); i++)
                        if(level(var(clause[i])) > level(var(clause[max_index])))
                        max_index = i;
                    Lit p = clause[1];
                    clause[1] = clause[max_index];
                    clause[max_index] = p;
                    }

                    if (verbosity >= 2)
                    {
                    printf("Keeping clause ");
                    for(int i=0; i<clause.size(); i++)
                    {   printf("%s%d ", sign(clause[i]) ? "-" : "", var(clause[i])+1);
                    }
                    printf("0\n");
                    }

                    CRef confl_clause = ca.alloc(clause, false);
                    attachClause(confl_clause);
                    clauses.push(confl_clause);
                }

                return;
            }
        }
    }

#ifdef UNEMBED_SUBGRAPH_CHECK
#ifdef OPT_START_GUB
    for(int g=opt_start_gub; g<opt_check_gub; g++)
#else
    for(int g=0; g<opt_check_gub; g++)
#endif
    {
        int p[12]; // If an umembeddable subgraph is found, p will contain which rows of M correspond with the rows of the lex greatest representation of the unembeddable subgraph
        int P[n];
        for(int j=0; j<n; j++) P[j] = -1;

        const double before = cpuTime();
        bool ret = has_gub_subgraph(n, P, p, g);
        const double after = cpuTime();
        gubtime += (after-before);

        // If graph has gub subgraph
        if (ret) {
            gubcount++;
            gubcounts[g]++;
            out_learnts.push();
            int c = 0;
            for(int jj=0; jj<n; jj++) {
                for(int ii=0; ii<jj; ii++) {
                    if(assigns[c]==l_True && P[jj] != -1 && P[ii] != -1)
                        if((P[ii] < P[jj] && gub[g][P[ii] + P[jj]*(P[jj]-1)/2]) || (P[jj] < P[ii] && gub[g][P[jj] + P[ii]*(P[ii]-1)/2]))
                            out_learnts[0].push(mkLit(c, true));
                    c++;
                }
            }
            /*for(int j = 0; j < n*(n-1)/2; j++) {
                if(assigns[j]==l_True)
                    out_learnts[0].push(mkLit(j, true));
            }*/
            if(guboutfile != NULL) {
                //fprintf(guboutfile, "a ");
                int c = 0;
                for(int jj=0; jj<n; jj++) {
                    for(int ii=0; ii<jj; ii++) {
                        if(assigns[c]==l_True && P[jj] != -1 && P[ii] != -1)
                            if((P[ii] < P[jj] && gub[g][P[ii] + P[jj]*(P[jj]-1)/2]) || (P[jj] < P[ii] && gub[g][P[jj] + P[ii]*(P[ii]-1)/2]))
                                fprintf(guboutfile, "-%d ", c+1);
                        c++;
                    }
                }
                /*for(int j = 0; j < n*(n-1)/2; j++)
                    if(assigns[j]==l_True)
                        fprintf(guboutfile, "%d ", j+1);
                */
                fprintf(guboutfile, "0\n");
                fflush(guboutfile);
            }
            if(permoutfile != NULL) {
                fprintf(permoutfile, "Minimal unembeddable subgraph %d:", g);
                int mii = 10;
                if(g >= 2 && g < 7)
                    mii = 11;
                else if(g >= 7)
                    mii = 12;
                for(int ii=0; ii<mii; ii++) {
                    fprintf(permoutfile, "%s%d", ii == 0 ? "" : " ", p[ii]);
                }
                fprintf(permoutfile, "\n");
            }
            return;
        }
    }
#endif

    // Verify that a complete solution has been found (and compute its hash)
    if(opt_skip_last > 0 || n == 0)
    {
        hash = 0;
        for(int i=0; i<max_exhaust_var; i++)
        {   //printf("%c", assigns[i]==l_True ? '1' : (assigns[i]==l_False ? '0' : '?'));
            if(assigns[i]==l_Undef)
                return;
            if(assigns[i]==l_True)
                hash += hash_values[i];
        }
        //printf("\n");
    }

    // Found a new complete solution
    if(exhauststring != NULL)
    {
        out_learnts.push();

        for(int i=0; i<max_exhaust_var; i++)
        {   
            //if(opt_fixed_card && assigns[i]!=l_True)
            //    continue;
            out_learnts[0].push(mkLit(i, assigns[i]==l_True));
        }

        if(permoutfile != NULL) {
            fprintf(permoutfile, "Complete solution\n");
        }

        // If this solution has not been seen before then output it
        if(solution_hashes.find(hash) == solution_hashes.end())
        {
            fprintf(exhaustfile, "a ");
            for(int i=0; i<max_exhaust_var; i++)
                fprintf(exhaustfile, "%s%d ", assigns[i]==l_True ? "" : "-", i+1);
            fprintf(exhaustfile, "0\n");
            fflush(exhaustfile);
            numsols++;
            solution_hashes.insert(hash);
        }

        // Add the learned clause to the vector of original clauses if the 'keep blocking' option enabled
        if(opt_keep_blocking==2)
        {
            vec<Lit> clause;
            out_learnts[0].copyTo(clause);
            {
                int max_index = 0;
                for(int i=1; i<clause.size(); i++)
                    if(level(var(clause[i])) > level(var(clause[max_index])))
                        max_index = i;
                Lit p = clause[0];
                clause[0] = clause[max_index];
                clause[max_index] = p;
            }

            {
                int max_index = 1;
                for(int i=2; i<clause.size(); i++)
                    if(level(var(clause[i])) > level(var(clause[max_index])))
                        max_index = i;
                Lit p = clause[1];
                clause[1] = clause[max_index];
                clause[max_index] = p;
            }

            if (verbosity >= 2)
            {
                printf("Keeping clause ");
                for(int i=0; i<clause.size(); i++)
                {   printf("%s%d ", sign(clause[i]) ? "-" : "", var(clause[i])+1);
                }
                printf("0\n");
            }

            CRef confl_clause = ca.alloc(clause, false);
            attachClause(confl_clause);
            clauses.push(confl_clause);
        }
    }
}

bool Solver::assertingClause(CRef confl) {
    Clause& c = ca[confl];
    int asserting = -1;
    for (int i = 0; i < c.size(); i++) {
        if (value(c[i]) == l_Undef) {
            if (asserting != -1) return false;
            asserting = i;
        }
    }
    return asserting == 0;
}

void Solver::analyze(vec<Lit>& conflvec, vec<Lit>& out_learnt, int& out_btlevel)
{
    int pathC = 0;
    CRef confl;
    Lit p     = lit_Undef;

    int cur_max = level(var(conflvec[0]));
    for(int j=1; j < conflvec.size(); j++) {
        if(level(var(conflvec[j])) > cur_max) {
            cur_max = level(var(conflvec[j]));
        }
    }
    if(cur_max == 0) {
        out_btlevel = -1;
        return;
    }
    if (conflvec.size() == 1) {
        out_btlevel = 0;
        conflvec.copyTo(out_learnt);
        return;
    }

    // Generate conflict clause:
    //
    out_learnt.push();      // (leave room for the asserting literal)
    int index   = trail.size() - 1;

        for (int j = (p == lit_Undef) ? 0 : 1; j < conflvec.size(); j++){
            Lit q = conflvec[j];

            if (!seen[var(q)] && level(var(q)) > 0){
#if BRANCHING_HEURISTIC == CHB
                last_conflict[var(q)] = conflicts;
#elif BRANCHING_HEURISTIC == VSIDS
                varBumpActivity(var(q));
#endif
                conflicted[var(q)]++;
                seen[var(q)] = 1;
                if (level(var(q)) >= cur_max)
                    pathC++;
                else
                    out_learnt.push(q);
            }
        }

        // Select next clause to look at:
        while (!seen[var(trail[index--])]);
        p     = trail[index+1];
        confl = reason(var(p));
        seen[var(p)] = 0;
        pathC--;

    while(pathC > 0){
        assert(confl != CRef_Undef); // (otherwise should be UIP)
        Clause& c = ca[confl];

#if LBD_BASED_CLAUSE_DELETION
        if (c.learnt() && c.activity() > 2)
            c.activity() = lbd(c);
#else
        if (c.learnt())
            claBumpActivity(c);
#endif

        for (int j = (p == lit_Undef) ? 0 : 1; j < c.size(); j++){
            Lit q = c[j];

            if (!seen[var(q)] && level(var(q)) > 0){
#if BRANCHING_HEURISTIC == CHB
                last_conflict[var(q)] = conflicts;
#elif BRANCHING_HEURISTIC == VSIDS
                varBumpActivity(var(q));
#endif
                conflicted[var(q)]++;
                seen[var(q)] = 1;
                if (level(var(q)) >= cur_max)
                    pathC++;
                else
                    out_learnt.push(q);
            }
        }

        // Select next clause to look at:
        while (!seen[var(trail[index--])]);
        p     = trail[index+1];
        confl = reason(var(p));
        seen[var(p)] = 0;
        pathC--;

    }
    out_learnt[0] = ~p;

    // Simplify conflict clause:
    //
    int i, j;
    out_learnt.copyTo(analyze_toclear);
    if (ccmin_mode == 2){
        uint32_t abstract_level = 0;
        for (i = 1; i < out_learnt.size(); i++)
            abstract_level |= abstractLevel(var(out_learnt[i])); // (maintain an abstraction of levels involved in conflict)

        for (i = j = 1; i < out_learnt.size(); i++)
            if (reason(var(out_learnt[i])) == CRef_Undef || !litRedundant(out_learnt[i], abstract_level))
                out_learnt[j++] = out_learnt[i];

    }else if (ccmin_mode == 1){
        for (i = j = 1; i < out_learnt.size(); i++){
            Var x = var(out_learnt[i]);

            if (reason(x) == CRef_Undef)
                out_learnt[j++] = out_learnt[i];
            else{
                Clause& c = ca[reason(var(out_learnt[i]))];
                for (int k = 1; k < c.size(); k++)
                    if (!seen[var(c[k])] && level(var(c[k])) > 0){
                        out_learnt[j++] = out_learnt[i];
                        break; }
            }
        }
    }else
        i = j = out_learnt.size();

    max_literals += out_learnt.size();
    out_learnt.shrink(i - j);
    tot_literals += out_learnt.size();

    // Find correct backtrack level:
    //
    if (out_learnt.size() == 1)
        out_btlevel = 0;
    else{
        int max_i = 1;
        // Find the first literal assigned at the next-highest level:
        for (int i = 2; i < out_learnt.size(); i++)
            if (level(var(out_learnt[i])) > level(var(out_learnt[max_i])))
                max_i = i;
        // Swap-in this literal at index 1:
        Lit p             = out_learnt[max_i];
        out_learnt[max_i] = out_learnt[1];
        out_learnt[1]     = p;
        out_btlevel       = level(var(p));
    }

#if ALMOST_CONFLICT
    seen[var(p)] = true;
    for(int i = out_learnt.size() - 1; i >= 0; i--) {
        Var v = var(out_learnt[i]);
        CRef rea = reason(v);
        if (rea != CRef_Undef) {
            Clause& reaC = ca[rea];
            for (int i = 0; i < reaC.size(); i++) {
                Lit l = reaC[i];
                if (!seen[var(l)]) {
                    seen[var(l)] = true;
                    almost_conflicted[var(l)]++;
                    analyze_toclear.push(l);
                }
            }
        }
    }
#endif
    for (int j = 0; j < analyze_toclear.size(); j++) seen[var(analyze_toclear[j])] = 0;    // ('seen[]' is now cleared)
}

/*_________________________________________________________________________________________________
|
|  analyze : (confl : Clause*) (out_learnt : vec<Lit>&) (out_btlevel : int&)  ->  [void]
|  
|  Description:
|    Analyze conflict and produce a reason clause.
|  
|    Pre-conditions:
|      * 'out_learnt' is assumed to be cleared.
|      * Current decision level must be greater than root level.
|  
|    Post-conditions:
|      * 'out_learnt[0]' is the asserting literal at level 'out_btlevel'.
|      * If out_learnt.size() > 1 then 'out_learnt[1]' has the greatest decision level of the 
|        rest of literals. There may be others from the same level though.
|  
|________________________________________________________________________________________________@*/
void Solver::analyze(CRef confl, vec<Lit>& out_learnt, int& out_btlevel)
{
    int pathC = 0;
    Lit p     = lit_Undef;

    // Generate conflict clause:
    //
    out_learnt.push();      // (leave room for the asserting literal)
    int index   = trail.size() - 1;

    do{
        assert(confl != CRef_Undef); // (otherwise should be UIP)
        Clause& c = ca[confl];

#if LBD_BASED_CLAUSE_DELETION
        if (c.learnt() && c.activity() > 2)
            c.activity() = lbd(c);
#else
        if (c.learnt())
            claBumpActivity(c);
#endif

        for (int j = (p == lit_Undef) ? 0 : 1; j < c.size(); j++){
            Lit q = c[j];

            if (!seen[var(q)] && level(var(q)) > 0){
#if BRANCHING_HEURISTIC == CHB
                last_conflict[var(q)] = conflicts;
#elif BRANCHING_HEURISTIC == VSIDS
                varBumpActivity(var(q));
#endif
                conflicted[var(q)]++;
                seen[var(q)] = 1;
                if (level(var(q)) >= decisionLevel())
                    pathC++;
                else
                    out_learnt.push(q);
            }
        }
        
        // Select next clause to look at:
        while (!seen[var(trail[index--])]);
        p     = trail[index+1];
        confl = reason(var(p));
        seen[var(p)] = 0;
        pathC--;

    }while (pathC > 0);
    out_learnt[0] = ~p;

    // Simplify conflict clause:
    //
    int i, j;
    out_learnt.copyTo(analyze_toclear);
    if (ccmin_mode == 2){
        uint32_t abstract_level = 0;
        for (i = 1; i < out_learnt.size(); i++)
            abstract_level |= abstractLevel(var(out_learnt[i])); // (maintain an abstraction of levels involved in conflict)

        for (i = j = 1; i < out_learnt.size(); i++)
            if (reason(var(out_learnt[i])) == CRef_Undef || !litRedundant(out_learnt[i], abstract_level))
                out_learnt[j++] = out_learnt[i];
        
    }else if (ccmin_mode == 1){
        for (i = j = 1; i < out_learnt.size(); i++){
            Var x = var(out_learnt[i]);

            if (reason(x) == CRef_Undef)
                out_learnt[j++] = out_learnt[i];
            else{
                Clause& c = ca[reason(var(out_learnt[i]))];
                for (int k = 1; k < c.size(); k++)
                    if (!seen[var(c[k])] && level(var(c[k])) > 0){
                        out_learnt[j++] = out_learnt[i];
                        break; }
            }
        }
    }else
        i = j = out_learnt.size();

    max_literals += out_learnt.size();
    out_learnt.shrink(i - j);
    tot_literals += out_learnt.size();

    // Find correct backtrack level:
    //
    if (out_learnt.size() == 1)
        out_btlevel = 0;
    else{
        int max_i = 1;
        // Find the first literal assigned at the next-highest level:
        for (int i = 2; i < out_learnt.size(); i++)
            if (level(var(out_learnt[i])) > level(var(out_learnt[max_i])))
                max_i = i;
        // Swap-in this literal at index 1:
        Lit p             = out_learnt[max_i];
        out_learnt[max_i] = out_learnt[1];
        out_learnt[1]     = p;
        out_btlevel       = level(var(p));
    }

#if ALMOST_CONFLICT
    seen[var(p)] = true;
    for(int i = out_learnt.size() - 1; i >= 0; i--) {
        Var v = var(out_learnt[i]);
        CRef rea = reason(v);
        if (rea != CRef_Undef) {
            Clause& reaC = ca[rea];
            for (int i = 0; i < reaC.size(); i++) {
                Lit l = reaC[i];
                if (!seen[var(l)]) {
                    seen[var(l)] = true;
                    almost_conflicted[var(l)]++;
                    analyze_toclear.push(l);
                }
            }
        }
    }
#endif
    for (int j = 0; j < analyze_toclear.size(); j++) seen[var(analyze_toclear[j])] = 0;    // ('seen[]' is now cleared)
}


// Check if 'p' can be removed. 'abstract_levels' is used to abort early if the algorithm is
// visiting literals at levels that cannot be removed later.
bool Solver::litRedundant(Lit p, uint32_t abstract_levels)
{
    analyze_stack.clear(); analyze_stack.push(p);
    int top = analyze_toclear.size();
    while (analyze_stack.size() > 0){
        assert(reason(var(analyze_stack.last())) != CRef_Undef);
        Clause& c = ca[reason(var(analyze_stack.last()))]; analyze_stack.pop();

        for (int i = 1; i < c.size(); i++){
            Lit p  = c[i];
            if (!seen[var(p)] && level(var(p)) > 0){
                if (reason(var(p)) != CRef_Undef && (abstractLevel(var(p)) & abstract_levels) != 0){
                    seen[var(p)] = 1;
                    analyze_stack.push(p);
                    analyze_toclear.push(p);
                }else{
                    for (int j = top; j < analyze_toclear.size(); j++)
                        seen[var(analyze_toclear[j])] = 0;
                    analyze_toclear.shrink(analyze_toclear.size() - top);
                    return false;
                }
            }
        }
    }

    return true;
}


/*_________________________________________________________________________________________________
|
|  analyzeFinal : (p : Lit)  ->  [void]
|  
|  Description:
|    Specialized analysis procedure to express the final conflict in terms of assumptions.
|    Calculates the (possibly empty) set of assumptions that led to the assignment of 'p', and
|    stores the result in 'out_conflict'.
|________________________________________________________________________________________________@*/
void Solver::analyzeFinal(Lit p, vec<Lit>& out_conflict)
{
    out_conflict.clear();
    out_conflict.push(p);

    if (decisionLevel() == 0)
        return;

    seen[var(p)] = 1;

    for (int i = trail.size()-1; i >= trail_lim[0]; i--){
        Var x = var(trail[i]);
        if (seen[x]){
            if (reason(x) == CRef_Undef){
                assert(level(x) > 0);
                out_conflict.push(~trail[i]);
            }else{
                Clause& c = ca[reason(x)];
                for (int j = 1; j < c.size(); j++)
                    if (level(var(c[j])) > 0)
                        seen[var(c[j])] = 1;
            }
            seen[x] = 0;
        }
    }

    seen[var(p)] = 0;
}


void Solver::uncheckedEnqueue(Lit p, CRef from)
{
    assert(value(p) == l_Undef);
    picked[var(p)] = conflicts;
#if ANTI_EXPLORATION
    uint64_t age = conflicts - canceled[var(p)];
    if (age > 0) {
        double decay = pow(0.95, age);
        activity[var(p)] *= decay;
        if (order_heap.inHeap(var(p))) {
            order_heap.increase(var(p));
        }
    }
#endif
    conflicted[var(p)] = 0;
#if ALMOST_CONFLICT
    almost_conflicted[var(p)] = 0;
#endif
    assigns[var(p)] = lbool(!sign(p));
    vardata[var(p)] = mkVarData(from, decisionLevel());
    trail.push_(p);
}


/*_________________________________________________________________________________________________
|
|  propagate : [void]  ->  [Clause*]
|  
|  Description:
|    Propagates all enqueued facts. If a conflict arises, the conflicting clause is returned,
|    otherwise CRef_Undef.
|  
|    Post-conditions:
|      * the propagation queue is empty, even if there was a conflict.
|________________________________________________________________________________________________@*/
CRef Solver::propagate()
{
    CRef    confl     = CRef_Undef;
    int     num_props = 0;
    watches.cleanAll();

    while (qhead < trail.size()){
        Lit            p   = trail[qhead++];     // 'p' is enqueued fact to propagate.
        vec<Watcher>&  ws  = watches[p];
        Watcher        *i, *j, *end;
        num_props++;

        for (i = j = (Watcher*)ws, end = i + ws.size();  i != end;){
            // Try to avoid inspecting the clause:
            Lit blocker = i->blocker;
            if (value(blocker) == l_True){
                *j++ = *i++; continue; }

            // Make sure the false literal is data[1]:
            CRef     cr        = i->cref;
            Clause&  c         = ca[cr];
            Lit      false_lit = ~p;
            if (c[0] == false_lit)
                c[0] = c[1], c[1] = false_lit;
            assert(c[1] == false_lit);
            i++;

            // If 0th watch is true, then clause is already satisfied.
            Lit     first = c[0];
            Watcher w     = Watcher(cr, first);
            if (first != blocker && value(first) == l_True){
                *j++ = w; continue; }

            // Look for new watch:
            for (int k = 2; k < c.size(); k++)
                if (value(c[k]) != l_False){
                    c[1] = c[k]; c[k] = false_lit;
                    watches[~c[1]].push(w);
                    goto NextClause; }

            // Did not find watch -- clause is unit under assignment:
            *j++ = w;
            if (value(first) == l_False){
                confl = cr;
                qhead = trail.size();
                // Copy the remaining watches:
                while (i < end)
                    *j++ = *i++;
            }else
                uncheckedEnqueue(first, cr);

        NextClause:;
        }
        ws.shrink(i - j);
    }
    propagations += num_props;
    simpDB_props -= num_props;

    return confl;
}

/*_________________________________________________________________________________________________
|
|  reduceDB : ()  ->  [void]
|  
|  Description:
|    Remove half of the learnt clauses, minus the clauses locked by the current assignment. Locked
|    clauses are clauses that are reason to some assignment. Binary clauses are never removed.
|________________________________________________________________________________________________@*/
struct reduceDB_lt { 
    ClauseAllocator& ca;
#if LBD_BASED_CLAUSE_DELETION
    vec<double>& activity;
    reduceDB_lt(ClauseAllocator& ca_,vec<double>& activity_) : ca(ca_), activity(activity_) {}
#else
    reduceDB_lt(ClauseAllocator& ca_) : ca(ca_) {}
#endif
    bool operator () (CRef x, CRef y) { 
#if LBD_BASED_CLAUSE_DELETION
        return ca[x].activity() > ca[y].activity();
    }
#else
        return ca[x].size() > 2 && (ca[y].size() == 2 || ca[x].activity() < ca[y].activity()); } 
#endif
};
void Solver::reduceDB()
{
    int     i, j;
#if LBD_BASED_CLAUSE_DELETION
    sort(learnts, reduceDB_lt(ca, activity));
#else
    double  extra_lim = cla_inc / learnts.size();    // Remove any clause below this activity
    sort(learnts, reduceDB_lt(ca));
#endif

    // Don't delete binary or locked clauses. From the rest, delete clauses from the first half
    // and clauses with activity smaller than 'extra_lim':
#if LBD_BASED_CLAUSE_DELETION
    for (i = j = 0; i < learnts.size(); i++){
        Clause& c = ca[learnts[i]];
        if (c.activity() > 2 && !locked(c) && i < learnts.size() / 2)
#else
    for (i = j = 0; i < learnts.size(); i++){
        Clause& c = ca[learnts[i]];
        if (c.size() > 2 && !locked(c) && (i < learnts.size() / 2 || c.activity() < extra_lim))
#endif
            removeClause(learnts[i]);
        else
            learnts[j++] = learnts[i];
    }
    learnts.shrink(i - j);
    checkGarbage();
}


void Solver::removeSatisfied(vec<CRef>& cs)
{
    int i, j;
    for (i = j = 0; i < cs.size(); i++){
        Clause& c = ca[cs[i]];
        if (satisfied(c))
            removeClause(cs[i]);
        else
            cs[j++] = cs[i];
    }
    cs.shrink(i - j);
}


void Solver::rebuildOrderHeap()
{
    vec<Var> vs;
    for (Var v = 0; v < nVars(); v++)
        if (decision[v] && value(v) == l_Undef)
            vs.push(v);
    order_heap.build(vs);
}


/*_________________________________________________________________________________________________
|
|  simplify : [void]  ->  [bool]
|  
|  Description:
|    Simplify the clause database according to the current top-level assigment. Currently, the only
|    thing done here is the removal of satisfied clauses, but more things can be put here.
|________________________________________________________________________________________________@*/
bool Solver::simplify()
{
    assert(decisionLevel() == 0);

    if (!ok || propagate() != CRef_Undef)
        return ok = false;

    if (nAssigns() == simpDB_assigns || (simpDB_props > 0))
        return true;

    // Remove satisfied clauses:
    removeSatisfied(learnts);
    if (remove_satisfied)        // Can be turned off.
        removeSatisfied(clauses);
    checkGarbage();
    rebuildOrderHeap();

    simpDB_assigns = nAssigns();
    simpDB_props   = clauses_literals + learnts_literals;   // (shouldn't depend on stats really, but it will do for now)

    return true;
}

/*_________________________________________________________________________________________________
|
|  search : (nof_conflicts : int) (params : const SearchParams&)  ->  [lbool]
|  
|  Description:
|    Search for a model the specified number of conflicts. 
|    NOTE! Use negative value for 'nof_conflicts' indicate infinity.
|  
|  Output:
|    'l_True' if a partial assigment that is consistent with respect to the clauseset is found. If
|    all variables are decision variables, this means that the clause set is satisfiable. 'l_False'
|    if the clause set is unsatisfiable. 'l_Undef' if the bound on number of conflicts is reached.
|________________________________________________________________________________________________@*/
lbool Solver::search(int nof_conflicts)
{
    assert(ok);
    int         backtrack_level;
    int         conflictC = 0;
    vec<Lit>    learnt_clause;
    vec<Lit>    units;
    starts++;

    for (;;){
        CRef confl = propagate();

#if BRANCHING_HEURISTIC == CHB
        double multiplier = confl == CRef_Undef ? reward_multiplier : 1.0;
        for (int a = action; a < trail.size(); a++) {
            Var v = var(trail[a]);
            uint64_t age = conflicts - last_conflict[v] + 1;
            double reward = multiplier / age ;
            double old_activity = activity[v];
            activity[v] = step_size * reward + ((1 - step_size) * old_activity);
            if (order_heap.inHeap(v)) {
                if (activity[v] > old_activity)
                    order_heap.decrease(v);
                else
                    order_heap.increase(v);
            }
        }
#endif
        if (confl != CRef_Undef){
            // CONFLICT
            conflicts++; conflictC++;
            if ((opt_max_conflicts > 0 && conflicts >= opt_max_conflicts) || (opt_max_proof_size > 0 && proofsize > opt_max_proof_size * 1048576l)) {
                interrupt();
            }
#if BRANCHING_HEURISTIC == CHB || BRANCHING_HEURISTIC == LRB
            if (step_size > min_step_size)
                step_size -= step_size_dec;
#endif
            if (decisionLevel() == 0) return l_False;

            learnt_clause.clear();
            analyze(confl, learnt_clause, backtrack_level);

            cancelUntil(backtrack_level);

#if BRANCHING_HEURISTIC == CHB
            action = trail.size();
#endif

            if(shortoutfile && learnt_clause.size() == 1) fprintf(shortoutfile, "%i 0\n", (var(learnt_clause[0]) + 1) * (-2 * sign(learnt_clause[0]) + 1));
            else if(shortoutfile && learnt_clause.size() == 2) fprintf(shortoutfile, "%i %i 0\n", (var(learnt_clause[0]) + 1) * (-2 * sign(learnt_clause[0]) + 1), (var(learnt_clause[1]) + 1) * (-2 * sign(learnt_clause[1]) + 1));
            if (learnt_clause.size() <= 1){
                uncheckedEnqueue(learnt_clause[0]);
            }else{
                CRef cr = ca.alloc(learnt_clause, true);
                learnts.push(cr);
                attachClause(cr);
#if LBD_BASED_CLAUSE_DELETION
                Clause& clause = ca[cr];
                clause.activity() = lbd(clause);
#else
                claBumpActivity(ca[cr]);
#endif
                uncheckedEnqueue(learnt_clause[0], cr);
            }
            if (output != NULL) {
              for (int i = 0; i < learnt_clause.size(); i++)
                fprintf(output, "%i " , (var(learnt_clause[i]) + 1) *
                                  (-2 * sign(learnt_clause[i]) + 1) );
              fprintf(output, "0\n");
            }
            proofsize += clausestrlen(learnt_clause);

#if BRANCHING_HEURISTIC == VSIDS
            varDecayActivity();
#endif
#if ! LBD_BASED_CLAUSE_DELETION
            claDecayActivity();
#endif

            if (--learntsize_adjust_cnt == 0){
                learntsize_adjust_confl *= learntsize_adjust_inc;
                learntsize_adjust_cnt    = (int)learntsize_adjust_confl;
#if ! RAPID_DELETION
                max_learnts             *= learntsize_inc;
#endif

                if (verbosity >= 1)
                {
                    printf("| %9d | %7d %8d %8d | %8d %8d %6.0f | %8ld | %9ld %9ld",
                           (int)conflicts, 
                           (int)dec_vars - (trail_lim.size() == 0 ? trail.size() : trail_lim[0]), nClauses(), (int)clauses_literals, 
                           (int)max_learnts, nLearnts(), (double)learnts_literals/nLearnts(), numsols, canon, noncanon);
                    if(opt_check_gub > 0)
                        printf(" %8ld", gubcount);
                    printf(" |\n");
                    fflush(stdout);
                }
            }

        }else{
            // NO CONFLICT
            if (nof_conflicts >= 0 && conflictC >= nof_conflicts || !withinBudget()){
                // Reached bound on number of conflicts:
                progress_estimate = progressEstimate();
                cancelUntil(0);
                return l_Undef; }

            // Simplify the set of problem clauses:
            if (decisionLevel() == 0 && !simplify())
                return l_False;

            /*if (learnts.size()-nAssigns() >= max_learnts) {
                // Reduce the set of learnt clauses:
                reduceDB();
#if RAPID_DELETION
                max_learnts += 500;
#endif
            }*/

            // Perform clause database reduction !
            if(conflicts >=  curRestart * nbclausesbeforereduce)
            {
                assert(learnts.size()>0);
                curRestart = (conflicts / nbclausesbeforereduce) + 1;
                reduceDB();
                reductions++;
                nbclausesbeforereduce += incReduceDB;
                max_learnts = nLearnts()+(curRestart*nbclausesbeforereduce)-conflicts;
            }

            Lit next = lit_Undef;
            while (decisionLevel() < assumptions.size()){
                // Perform user provided assumption:
                Lit p = assumptions[decisionLevel()];
                if (value(p) == l_True){
                    // Dummy decision level:
                    newDecisionLevel();
                }else if (value(p) == l_False){
                    analyzeFinal(~p, conflict);
                    cancelUntil(0);
                    addClause_(conflict);
                    if (output != NULL) {
                      for (int i = 0; i < conflict.size(); i++)
                        fprintf(output, "%i " , (var(conflict[i]) + 1) *
                                          (-2 * sign(conflict[i]) + 1) );
                      fprintf(output, "0\n");
                    }
                    proofsize += clausestrlen(conflict);
#if DATABASE_REDUCTION_EVERY_CUBE
                    reduceDB();
                    reductions++;
                    nbclausesbeforereduce += incReduceDB;
                    max_learnts = nLearnts()+(curRestart*nbclausesbeforereduce)-conflicts;
#else
                    nbclausesbeforereduce = firstReduceDB;
#endif
                    return l_False;
                }else{
                    next = p;
                    break;
                }
            }

            if (next == lit_Undef){
                // New variable decision:
                decisions++;
                next = pickBranchLit();

                callbackLearntClauses.clear();
                callbackFunction(next == lit_Undef, callbackLearntClauses);
                if (callbackLearntClauses.size() > 0) {
                    conflicts++; conflictC++;
                    int pending = learnts.size();
                    units.clear();
                    backtrack_level = decisionLevel();
                    for (int i = 0; i < callbackLearntClauses.size(); i++) {
                        int curlevel;
                        learnt_clause.clear();
                        if (output != NULL /*&& opt_trust_blocking*/) {
                          fprintf(output, "t ");
                          for (int j = 0; j < callbackLearntClauses[i].size(); j++)
                            fprintf(output, "%i " , (var(callbackLearntClauses[i][j]) + 1) *
                                              (-2 * sign(callbackLearntClauses[i][j]) + 1) );
                          fprintf(output, "0\n");
                        }
                        proofsize += 2+clausestrlen(callbackLearntClauses[i]);
                        analyze(callbackLearntClauses[i], learnt_clause, curlevel);
                        if (output != NULL) {
                          for (int j = 0; j < learnt_clause.size(); j++)
                            fprintf(output, "%i " , (var(learnt_clause[j]) + 1) *
                                              (-2 * sign(learnt_clause[j]) + 1) );
                          fprintf(output, "0\n");
                        }
                        proofsize += clausestrlen(learnt_clause);
                        if (output != NULL && opt_keep_blocking < 2) {
                          fprintf(output, "d ");
                          for (int j = 0; j < callbackLearntClauses[i].size(); j++)
                            fprintf(output, "%i " , (var(callbackLearntClauses[i][j]) + 1) *
                                              (-2 * sign(callbackLearntClauses[i][j]) + 1) );
                          fprintf(output, "0\n");
                        }
                        if(opt_keep_blocking < 2) {
                            proofsize += 2+clausestrlen(callbackLearntClauses[i]);
                        }
                        if (curlevel == -1) {
                            return l_False;
                        } else if (curlevel < backtrack_level) {
                            backtrack_level = curlevel;
                        }
                        if(shortoutfile && learnt_clause.size() == 1) fprintf(shortoutfile, "%i 0\n", (var(learnt_clause[0]) + 1) * (-2 * sign(learnt_clause[0]) + 1));
                        else if(shortoutfile && learnt_clause.size() == 2) fprintf(shortoutfile, "%i %i 0\n", (var(learnt_clause[0]) + 1) * (-2 * sign(learnt_clause[0]) + 1), (var(learnt_clause[1]) + 1) * (-2 * sign(learnt_clause[1]) + 1));
                        if (learnt_clause.size() <= 1) {
                            units.push(learnt_clause[0]);
                        } else {
                            // Add the learned clause (after minimization) to the vector of original clauses if the 'keep blocking' option enabled
                            if(opt_keep_blocking==1)
                            {
                                vec<Lit> clause;
                                learnt_clause.copyTo(clause);
                                {
                                    int max_index = 0;
                                    for(int i=1; i<clause.size(); i++)
                                        if(level(var(clause[i])) > level(var(clause[max_index])))
                                            max_index = i;
                                    Lit p = clause[0];
                                    clause[0] = clause[max_index];
                                    clause[max_index] = p;
                                }

                                {
                                    int max_index = 1;
                                    for(int i=2; i<clause.size(); i++)
                                        if(level(var(clause[i])) > level(var(clause[max_index])))
                                            max_index = i;
                                    Lit p = clause[1];
                                    clause[1] = clause[max_index];
                                    clause[max_index] = p;
                                }

                                if (verbosity >= 2)
                                {
                                    printf("Keeping minimized clause ");
                                    for(int i=0; i<clause.size(); i++)
                                    {   printf("%s%d ", sign(clause[i]) ? "-" : "", var(clause[i])+1);
                                    }
                                    printf("0\n");
                                }

                                CRef confl_clause = ca.alloc(clause, false);
                                attachClause(confl_clause);
                                clauses.push(confl_clause);
                            } else {
                                CRef cr = ca.alloc(learnt_clause, true);
                                learnts.push(cr);
                                attachClause(cr);
#if LBD_BASED_CLAUSE_DELETION
                                Clause& clause = ca[cr];
                                clause.activity() = lbd(clause);
#else
                                claBumpActivity(ca[cr]);
#endif
                            }
                        }
                    }

                    cancelUntil(backtrack_level);

#if BRANCHING_HEURISTIC == CHB
                    action = trail.size();
#endif

                    for (int i = 0; i < units.size(); i++) {
                        Lit l = units[i];
                        // Make sure it wasn't assigned by one of the other callback learnt clauses.
                        if (value(l) == l_Undef) uncheckedEnqueue(l);
                    }
                    for (int i = pending; i < learnts.size(); i++) {
                        CRef cr = learnts[i];
                        Clause& c = ca[cr];
                        bool asserting = assertingClause(cr);
                        if (asserting) uncheckedEnqueue(c[0], cr);
                    }
                    // Do not branch.
                    if (next != lit_Undef) {
                        insertVarOrder(var(next));
                        next = lit_Undef;
                    }
                } else if (next == lit_Undef)
                    // Model found:
                    return l_True;
            }

            if (next != lit_Undef) {
                // Increase decision level and enqueue 'next'
                newDecisionLevel();
    #if BRANCHING_HEURISTIC == CHB
                action = trail.size();
    #endif
                uncheckedEnqueue(next);
            }
        }
    }
}


double Solver::progressEstimate() const
{
    double  progress = 0;
    double  F = 1.0 / nVars();

    for (int i = 0; i <= decisionLevel(); i++){
        int beg = i == 0 ? 0 : trail_lim[i - 1];
        int end = i == decisionLevel() ? trail.size() : trail_lim[i];
        progress += pow(F, i) * (end - beg);
    }

    return progress / nVars();
}

/*
  Finite subsequences of the Luby-sequence:

  0: 1
  1: 1 1 2
  2: 1 1 2 1 1 2 4
  3: 1 1 2 1 1 2 4 1 1 2 1 1 2 4 8
  ...


 */

static double luby(double y, int x){

    // Find the finite subsequence that contains index 'x', and the
    // size of that subsequence:
    int size, seq;
    for (size = 1, seq = 0; size < x+1; seq++, size = 2*size+1);

    while (size-1 != x){
        size = (size-1)>>1;
        seq--;
        x = x % size;
    }

    return pow(y, seq);
}

// NOTE: assumptions passed in member-variable 'assumptions'.
lbool Solver::solve_()
{
    model.clear();
    conflict.clear();
    if (!ok) return l_False;

    solves++;

#if RAPID_DELETION
    max_learnts = nLearnts()+(curRestart*nbclausesbeforereduce)-conflicts;
#else
    max_learnts               = nClauses() * learntsize_factor;
#endif
    learntsize_adjust_confl   = learntsize_adjust_start_confl;
    learntsize_adjust_cnt     = (int)learntsize_adjust_confl;
    lbool   status            = l_Undef;

    if (verbosity >= 2){
        printf("LBD Based Clause Deletion : %d\n", LBD_BASED_CLAUSE_DELETION);
        printf("Rapid Deletion : %d\n", RAPID_DELETION);
        printf("Almost Conflict : %d\n", ALMOST_CONFLICT);
        printf("Anti Exploration : %d\n", ANTI_EXPLORATION);
    }
    if (verbosity >= 1 && !(opt_check_gub > 0)) {
        printf("============================[ Search Statistics ]====================================================\n");
        printf("| Conflicts |          ORIGINAL         |          LEARNT          | Num Sols |      SUBGRAPHS      |\n");
        printf("|           |    Vars  Clauses Literals |    Limit  Clauses Lit/Cl |          | Canonical Noncanon. |\n");
        printf("=====================================================================================================\n");
    } else if (verbosity >= 1) {
        printf("============================[ Search Statistics ]=============================================================\n");
        printf("| Conflicts |          ORIGINAL         |          LEARNT          | Num Sols |      SUBGRAPHS               |\n");
        printf("|           |    Vars  Clauses Literals |    Limit  Clauses Lit/Cl |          | Canonical Noncanon. Unembed. |\n");
        printf("==============================================================================================================\n");
    }

    // Search:
    int curr_restarts = 0;
    while (status == l_Undef){
        double rest_base = luby_restart ? luby(restart_inc, curr_restarts) : pow(restart_inc, curr_restarts);
        status = search(rest_base * restart_first);
        if (!withinBudget()) break;
        curr_restarts++;
    }

    if (verbosity >= 1)
    {   if(opt_check_gub > 0) printf("=========");
        printf("=====================================================================================================\n");
        printf("Number of solutions   : %ld\n", numsols);
        printf("Canonical subgraphs   : %-12"PRIu64"   (%.0f /sec)\n", canon, canon/canontime);
        for(int i=2; i<n; i++) {
#ifdef PERM_STATS
            printf("          order %2d    : %-12"PRIu64"   (%.0f /sec) %.0f avg. perms\n", i+1, canonarr[i], canonarr[i]/canontimearr[i], canon_np[i]/(float)(canonarr[i] > 0 ? canonarr[i] : 1));
#else
            printf("          order %2d    : %-12"PRIu64"   (%.0f /sec)\n", i+1, canonarr[i], canonarr[i]/canontimearr[i]);
#endif
        }
        printf("Noncanonical subgraphs: %-12"PRIu64"   (%.0f /sec)\n", noncanon, noncanon/noncanontime);
        for(int i=2; i<n; i++) {
#ifdef PERM_STATS
            printf("          order %2d    : %-12"PRIu64"   (%.0f /sec) %.0f avg. perms\n", i+1, noncanonarr[i], noncanonarr[i]/noncanontimearr[i], noncanon_np[i]/(float)(noncanonarr[i] > 0 ? noncanonarr[i] : 1));
#else
            printf("          order %2d    : %-12"PRIu64"   (%.0f /sec)\n", i+1, noncanonarr[i], noncanonarr[i]/noncanontimearr[i]);
#endif
        }
        printf("Canonicity checking   : %g s\n", canontime);
        printf("Noncanonicity checking: %g s\n", noncanontime);
        printf("Total canonicity time : %g s\n", canontime+noncanontime);
        if(opt_check_gub > 0) {
            printf("Unembeddable checking : %g s\n", gubtime);
            for(int g=0; g<opt_check_gub; g++) {
                printf("        graph #%2d     : %-12"PRIu64"\n", g, gubcounts[g]);
            }
            printf("Total unembed. graphs : %ld\n", gubcount);
        }
        printf("Proof size            : %ld bytes\n", proofsize);
    }


    if (status == l_True){
        // Extend & copy model:
        model.growTo(nVars());
        for (int i = 0; i < nVars(); i++) model[i] = value(i);
    }else if (status == l_False && conflict.size() == 0)
        ok = false;

    cancelUntil(0);
    return status;
}

//=================================================================================================
// Writing CNF to DIMACS:
// 
// FIXME: this needs to be rewritten completely.

static Var mapVar(Var x, vec<Var>& map, Var& max)
{
    if (map.size() <= x || map[x] == -1){
        map.growTo(x+1, -1);
        map[x] = max++;
    }
    return map[x];
}


void Solver::toDimacs(FILE* f, Clause& c, vec<Var>& map, Var& max)
{
    if (satisfied(c)) return;

    for (int i = 0; i < c.size(); i++)
        if (value(c[i]) != l_False)
            fprintf(f, "%s%d ", sign(c[i]) ? "-" : "", mapVar(var(c[i]), map, max)+1);
    fprintf(f, "0\n");
}


void Solver::toDimacs(const char *file, const vec<Lit>& assumps)
{
    FILE* f = fopen(file, "wr");
    if (f == NULL)
        fprintf(stderr, "could not open file %s\n", file), exit(1);
    toDimacs(f, assumps);
    fclose(f);
}


void Solver::toDimacs(FILE* f, const vec<Lit>& assumps)
{
    // Handle case when solver is in contradictory state:
    if (!ok){
        fprintf(f, "p cnf 1 2\n1 0\n-1 0\n");
        return; }

    vec<Var> map; Var max = 0;

    // Cannot use removeClauses here because it is not safe
    // to deallocate them at this point. Could be improved.
    int cnt = 0;
    for (int i = 0; i < clauses.size(); i++)
        if (!satisfied(ca[clauses[i]]))
            cnt++;
        
    for (int i = 0; i < clauses.size(); i++)
        if (!satisfied(ca[clauses[i]])){
            Clause& c = ca[clauses[i]];
            for (int j = 0; j < c.size(); j++)
                if (value(c[j]) != l_False)
                    mapVar(var(c[j]), map, max);
        }

    // Assumptions are added as unit clauses:
    cnt += assumptions.size();

    fprintf(f, "p cnf %d %d\n", max, cnt);

    for (int i = 0; i < assumptions.size(); i++){
        assert(value(assumptions[i]) != l_False);
        fprintf(f, "%s%d 0\n", sign(assumptions[i]) ? "-" : "", mapVar(var(assumptions[i]), map, max)+1);
    }

    for (int i = 0; i < clauses.size(); i++)
        toDimacs(f, ca[clauses[i]], map, max);

    if (verbosity > 0)
        printf("Wrote %d clauses with %d variables.\n", cnt, max);
}


//=================================================================================================
// Garbage Collection methods:

void Solver::relocAll(ClauseAllocator& to)
{
    // All watchers:
    //
    // for (int i = 0; i < watches.size(); i++)
    watches.cleanAll();
    for (int v = 0; v < nVars(); v++)
        for (int s = 0; s < 2; s++){
            Lit p = mkLit(v, s);
            // printf(" >>> RELOCING: %s%d\n", sign(p)?"-":"", var(p)+1);
            vec<Watcher>& ws = watches[p];
            for (int j = 0; j < ws.size(); j++)
                ca.reloc(ws[j].cref, to);
        }

    // All reasons:
    //
    for (int i = 0; i < trail.size(); i++){
        Var v = var(trail[i]);

        if (reason(v) != CRef_Undef && (ca[reason(v)].reloced() || locked(ca[reason(v)])))
            ca.reloc(vardata[v].reason, to);
    }

    // All learnt:
    //
    for (int i = 0; i < learnts.size(); i++)
        ca.reloc(learnts[i], to);

    // All original:
    //
    for (int i = 0; i < clauses.size(); i++)
        ca.reloc(clauses[i], to);
}


void Solver::garbageCollect()
{
    // Initialize the next region to a size corresponding to the estimated utilization degree. This
    // is not precise but should avoid some unnecessary reallocations for the new region:
    ClauseAllocator to(ca.size() - ca.wasted()); 

    relocAll(to);
    if (verbosity >= 2)
        printf("|  Garbage collection:   %12d bytes => %12d bytes             |\n", 
               ca.size()*ClauseAllocator::Unit_Size, to.size()*ClauseAllocator::Unit_Size);
    to.moveTo(ca);
}

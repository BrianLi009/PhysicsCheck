# kochen-specker-graph

## Research Log:

### Week 1: 
Besides implemeting the algorithm to check the embedibility of a graph based on the paper, I have been playing with previous results and trying to construct a new constraint for the search algorithm. Currently I have not made any progress. Currently what I am trying to do is to pass in a couple candidates into Sage, and try to find common properties of the graph. We'll see what happens.

Thoughts: Currently, the constraint applied in the paper is that, a minimal Kochen Specker system is **connected, squarefree, and has minimal vertex degree 3**. We could add the restriction that each vertex must be part of a triangle (Proposition 2.2). This is not too hard to implement and the runtime won't be too bad either. The real question is, how many graphs can we eliminate using this constraint?

Thoughts: We know that any non-010 colorable graph is also non-3 colorable, do we know any special properties for graphs with chromatic number greater than 3?

### Week 2:
The main objective for this week, is to implement the pySAT algorithm for the constraints. The pySAT installation process took me a while as pip does not seem to work for the package. After consulting [this issue](https://github.com/pysathq/pysat/issues/7), I was able to clone the package then install it.

Constraint 1: squarefree

Constraint 2: minimum degree is 3

Constraint 3 (harder to implement): all vertices are part of a triangle

### Week 3:
The objective for this week is to first debug the first two constraints, implement the third, which states that "every vertex is a part of a triangle subgraph". Then we combine all three constraints to generate graphs. After that, we should also code the SAT checker for non-010 colorable graph.

Finished all three constraints and now we can generate some graphs! We can also now check whether a graph is 010-colorable or not.

### Week 4:
I'll spend some of this week preparing a presentation. I have implemented the isomorphism block, but the main problem is it seems challenging to match the label. The isomorphism blocker labels variables by adjacency matrices, while the other constraints label by edges. We will have to address that.
Totally stucked on the isomorphism blocker, it doesn't seem to be blocking any graphs at all lol.

Note: as my work complicates throughout the weeks, I'm moving my progress log into overleaf LaTeX, and unfortunately those won't be avaialble for now.

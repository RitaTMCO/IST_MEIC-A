%--> Group: 07  --> Student: Rita Castro Oliveira

include "alldifferent.mzn";

%---------------------------------------|Variables|-----------------------------------------------
int: nvertices; %number of vertices
int: nedges; %number of edges
int: nagents; %number of agents
int: maxtimestep; %maximum time that each agent has to arrive to goal vertex
var 0..maxtimestep: makespan; %minimum number of time steps that are required to reach the goal position from the start position.
array[1..nagents] of 1..nvertices: start; % start position for each agent
array[1..nagents] of 1..nvertices: goal; % goal position for each agent
array[1..nagents, 0..maxtimestep] of var 1..nvertices: path; % path of each agent since start point to goal point of each time
array[1..nvertices] of set of 1..nvertices: edges;  % index of edges is id of vertex. Each index has the neighbors of vertex index and vertex index


%---------------------------------------|Constraints|-----------------------------------------------
% In time t = 0, agent is in initial vertex. In t = makespan and t = maxtimestep, agent must to be in goal vertex
constraint forall(a in 1..nagents) (path[a,0] = start[a] /\ path[a,makespan] = goal[a] /\ path[a,maxtimestep] = goal[a]);

% If in any number of timesteps all agents are in their goal position, then this number is the makespan.
constraint exists(t in 1..maxtimestep) (if forall(a in 1..nagents)(path[a,t] = goal[a]) then makespan=t endif);

% Test Transaction Validity from one vertex in time t to another vertex in time t+1.
constraint forall(a in 1..nagents,t in 0..maxtimestep-1) (path[a,t+1] in edges[path[a,t]]); 
       
% To avoid vertex conflict and edge conflict.       
constraint forall(t in 0..maxtimestep)(alldifferent( [ path[a,t] | a in 1..nagents]));

% To avoid Following conflict, Cycle conflict and Swapping conflict          
constraint forall(a in 1..nagents,t in 0..maxtimestep-1)(alldifferent( [path[a,t+1]] ++ [ path[a2,t] | a2 in 1..nagents diff{a}]));

         
%---------------------------------------|Solve|----------------------------------------------- 
% the objective is to minimize makespan                                                                           
solve minimize makespan;

output [if i=1 then "i=\(j)\t" endif ++
        if i = nagents then "\(i):" ++ show(path[i,j]) ++ "\n" else "\(i):" ++ show(path[i,j]) ++ "\t" endif | j in 0..fix(makespan), i in 1..nagents];
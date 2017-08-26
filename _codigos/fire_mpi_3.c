/* fire_mpi.c - final step
 * set up probabilities for each process, add MPI commands
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

#define UNBURNT 0
#define SMOLDERING 1
#define BURNING 2
#define BURNT 3

#define true 1
#define false 0

typedef int boolean;

extern void seed_by_time(int);
extern int ** allocate_forest(int);
extern void initialize_forest(int, int **);
extern double get_percent_burned(int, int **);
extern void delete_forest(int, int **);
extern void light_tree(int, int **,int,int);
extern boolean forest_is_burning(int, int **);
extern void forest_burns(int, int **,double);
extern void burn_until_out(int,int **,double,int,int);
extern void print_forest(int, int **);

MPI_Status status;
int rank;
int size;

#define min(X,Y) ((X) < (Y) ? (X) : (Y))

int main(int argc, char ** argv) {
    // initial conditions and variable definitions
    int forest_size=20;
    double prob_spread;
    double prob_min=0.0;
    double prob_max=1.0;
    double prob_step;
    int **forest;
    // add second loop index
    int i,j;
    double percent_burned;
    int i_trial;
    int n_trials=600;
    int i_prob;
    int i_start,i_finish;
    int n_probs=100;
    double * per_burns;
    // add storage array
    double * per_storage;

    // setup MPI
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD,&size);
    MPI_Comm_rank(MPI_COMM_WORLD,&rank);


    // setup problem, allocate memory
    seed_by_time(0);
    forest=allocate_forest(forest_size);
    per_burns = (double *)malloc(sizeof(double)*n_probs+1);
    // allocate storage array
    per_storage = (double *)malloc(sizeof(double)*n_probs+1);

    // for a number of probabilities, calculate
    // average burn and output
    prob_step = (prob_max-prob_min)/(double)(n_probs-1);
    // change loop to go from 0 to max
    for (i_prob = 0 ; i_prob < n_probs; i_prob++) {
        //for a number of trials, calculate average
        //percent burn
        prob_spread = prob_min + (double)i_prob * prob_step;
        percent_burned=0.0;
        // change loop to do fewer trials
        for (i_trial=0; i_trial < n_trials/size; i_trial++) {
            //burn until fire is gone
            burn_until_out(forest_size,forest,prob_spread,10,10);
            percent_burned+=get_percent_burned(forest_size,forest);
        }
        percent_burned/=n_trials;
        per_burns[i_prob]=percent_burned;

    }

    // communicate
    if (rank>0) {
        // send values from client to server
        MPI_Send(per_burns,n_probs,MPI_DOUBLE,
            0,rank,MPI_COMM_WORLD);
    } else {
        // for every client, recieve values into a buffer
        // so that you do not overwrite old calculations,
        // and update calculated values
        for (i = 1; i< size; i++) {
            MPI_Recv(per_storage,n_probs,MPI_DOUBLE,
                i,i,MPI_COMM_WORLD,&status);
            for (j=0;j<n_probs;j++) {
                per_burns[j]+=per_storage[j];
            }
        }
        // average over clients
        //for (j=0;j<n_probs;j++) {
            //per_burns[j]/=size;
        //}
        // print output
        printf("Probability of fire spreading, Average percent burned\n");
        for (i_prob =0 ; i_prob<n_probs; i_prob++) {
            prob_spread = prob_min + (double)i_prob * prob_step;
            printf("%lf , %lf\n",prob_spread,per_burns[i_prob]);
        }
    }

    // clean up
    delete_forest(forest_size,forest);
    free(per_burns);
    MPI_Finalize();


}

void seed_by_time(int offset) {
    time_t the_time;
    time(&the_time);
    srand((int)the_time+offset);
}

void burn_until_out(int forest_size,int ** forest, double prob_spread,
    int start_i, int start_j) {

    initialize_forest(forest_size,forest);
    light_tree(forest_size,forest,start_i,start_j);

    // burn until fire is gone
    while(forest_is_burning(forest_size,forest)) {
        forest_burns(forest_size,forest,prob_spread);
    }
}

double get_percent_burned(int forest_size,int ** forest) {
    int i,j;
    int total = forest_size*forest_size-1;
    int sum=0;

    // calculate pecrent burned
    for (i=0;i<forest_size;i++) {
        for (j=0;j<forest_size;j++) {
            if (forest[i][j]==BURNT) {
                sum++;
            }
        }
    }

    // return percent burned;
    return ((double)(sum-1)/(double)total);
}


int ** allocate_forest(int forest_size) {
    int i,j;
    int ** forest;

    forest = (int **) malloc (sizeof(int*)*forest_size);
    for (i=0;i<forest_size;i++) {
        forest[i] = (int *) malloc (sizeof(int)*forest_size);
    }

    return forest;
}

void initialize_forest(int forest_size, int ** forest) {
    int i,j;

    for (i=0;i<forest_size;i++) {
        for (j=0;j<forest_size;j++) {
            forest[i][j]=UNBURNT;
        }
    }
}

void delete_forest(int forest_size, int ** forest) {
    int i;

    for (i=0;i<forest_size;i++) {
        free(forest[i]);
    }
    free(forest);
}

void light_tree(int forest_size, int ** forest, int i, int j) {
    forest[i][j]=SMOLDERING;
}

boolean fire_spreads(double prob_spread) {
    if ((double)rand()/(double)RAND_MAX < prob_spread) 
        return true;
    else
        return false;
}

void forest_burns(int forest_size, int **forest,double prob_spread) {
    int i,j;
    extern boolean fire_spreads(double);

    //burning trees burn down, smoldering trees ignite
    for (i=0; i<forest_size; i++) {
        for (j=0;j<forest_size;j++) {
            if (forest[i][j]==BURNING) forest[i][j]=BURNT;
            if (forest[i][j]==SMOLDERING) forest[i][j]=BURNING;
        }
    }

    //unburnt trees catch fire
    for (i=0; i<forest_size; i++) {
        for (j=0;j<forest_size;j++) {
            if (forest[i][j]==BURNING) {
                if (i!=0) { // North
                    if (fire_spreads(prob_spread)&&forest[i-1][j]==UNBURNT) {
                        forest[i-1][j]=SMOLDERING;
                    }
                }
                if (i!=forest_size-1) { //South
                    if (fire_spreads(prob_spread)&&forest[i+1][j]==UNBURNT) {
                        forest[i+1][j]=SMOLDERING;
                    }
                }
                if (j!=0) { // West
                    if (fire_spreads(prob_spread)&&forest[i][j-1]==UNBURNT) {
                        forest[i][j-1]=SMOLDERING;
                    }
                }
                if (j!=forest_size-1) { // East
                    if (fire_spreads(prob_spread)&&forest[i][j+1]==UNBURNT) {
                        forest[i][j+1]=SMOLDERING;
                    }
                }
            }
        }
    }
}

boolean forest_is_burning(int forest_size, int ** forest) {
    int i,j;

    for (i=0; i<forest_size; i++) {
        for (j=0; j<forest_size; j++) {
            if (forest[i][j]==SMOLDERING||forest[i][j]==BURNING) {
                return true;
            }
        }
    }
    return false;
}

void print_forest(int forest_size,int ** forest) {
    int i,j;

    for (i=0;i<forest_size;i++) {
        for (j=0;j<forest_size;j++) {
            if (forest[i][j]==BURNT) {
                printf(".");
            } else {
                printf("X");
            }
        }
        printf("\n");
    }
}

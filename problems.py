'''
Defines each of the benchmark problems used as well as the function sets
for those problems.
'''
import operator
import itertools


def nand(x, y):
    '''
    Simple Nand function for inclusion in function sets.
    '''
    return not (x and y)


def nor(x, y):
    '''
    Simple Nor function for inclusion in function sets.
    '''
    return not (x or y)

# Standard lists of operators for different problems to use
binary_operators = [operator.or_, operator.and_, nand, nor]


class Problem(object):
    '''
    The abstract base of a problem
    '''
    def __init__(self, config):
        '''
        Designed to force children of this class to implement this function.
        Children use this function to set up problem specific initialization
        from configuration information.
        '''
        raise NotImplementedError()

    def get_fitness(self, individual):
        '''
        Designed to force children of this class to implement this function.
        Children use this function evaluate an individual and
        return its fitness.
        '''
        raise NotImplementedError()


class Bounded_Problem(object):
    '''
    Base object for any problem with a known set of test cases.  Stores a
    map for all possible inputs to their correct outputs so they only
    have to be evaluated once.
    '''

    def __init__(self, config):
        '''
        Create a new problem.

        Parameters:

        - ``config``: A dictionary containing the configuration information
          required to fully initialize the problem.  Should include values
          for:

          - Any configuration information required to construct the problem
            range.
          - ``epsilon``: The amount of allowed error on each test.
        '''
        self.config = config
        self.training = [(inputs, self.problem_function(inputs))
                         for inputs in self.data_range(config)]
        self.epsilon = config['epsilon']

    def get_fitness(self, individual):
        '''
        Return the fitness of an individual as applied to this problem.

        Parameters:

        - ``individual``: The individual to be evaluated.
        '''
        score = 0
        for inputs, outputs in self.training:
            answers = individual.evaluate(inputs)
            # Finds the average number of outputs more than epsilon away from
            # the correct output
            score += (sum(float(abs(answer - output) > self.epsilon)
                          for answer, output in zip(answers, outputs))
                      / len(outputs))
        # Returns the percentage of correct answers
        return 1 - (score / float(len(self.training)))

    def problem_function(self, _):
        '''
        Designed to force children of this class to implement this function.
        Children use this function to define how to translate an input value
        into an output value for their problem.
        '''
        raise NotImplementedError()


def binary_range(config):
    '''
    Given a dictionary specifying the ``input_length``, returns all binary
    values of that length.
    '''
    return itertools.product((0, 1), repeat=config['input_length'])


def single_bit_set(config):
    '''
    Creates the list of all possible binary strings of specified length
    with exactly one set bit.  ``config`` should specify the ``input_length``.
    '''
    return [map(int, '1'.rjust(i + 1, '0').ljust(config['input_length'], '0'))
            for i in range(config['input_length'])]


class Binary_Mixin(object):
    '''
    Inheritance mixin useful for setting the class attributes of
    binary problems.
    '''
    data_range = staticmethod(binary_range)
    operators = binary_operators
    max_arity = 2


class Neutral(Problem):
    '''
    Defines the Neutral problem, in which all individuals receive the same
    fitness.  The only operator in this function is 'None', meaning only
    connection genes actually evolve.
    '''
    operators = [None]
    max_arity = 2

    def __init__(self, _):
        '''
        Doesn't require initialization, but must implement.
        '''
        pass

    def get_fitness(self, _):
        '''
        Returns the fitness of passed in individual, which is always 0.
        '''
        return 0


class Binary_Multiply(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Binary Multiplier problem.
    '''
    def problem_function(self, inputs):
        '''
        Return the result of performing a binary multiplication of the first
        half of the inputs with the second half.  Will always have the same
        number of output bits as input bits.
        '''
        # convert the two binary numbers to integers
        joined = ''.join(map(str, inputs))
        middle = len(joined) / 2
        a, b = joined[:middle], joined[middle:]
        # multiply the two numbers and convert back to binary
        multiplied = bin(int(a, 2) * int(b, 2))[2:]
        # pad the result to have enough bits
        extended = multiplied.rjust(len(inputs), '0')
        return map(int, extended)


class Breadth(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Breadth problem.
    '''
    # Set the data range to be all possible inputs with a single set bit.
    data_range = staticmethod(single_bit_set)
    # Set the list of possible operators to just be OR.
    operators = [operator.or_]

    def problem_function(self, inputs):
        '''
        Returns true as long as at least one input is true.
        '''
        return [sum(inputs) > 0]


class Depth(Problem):
    '''
    Defines the Depth problem.
    '''
    # Set the list of possible operators to just be just min(X, Y) + 1.
    operators = [lambda X, Y: min(X, Y) + 1]
    max_arity = 2

    def __init__(self, config):
        '''
        Saves configuration for use during evaluation.
        '''
        self.config = config

    def get_fitness(self, individual):
        '''
        Returns the fitness of the individual as a percentage of maximum
        fitness.
        '''
        return individual.evaluate([0])[0] / float(self.config['graph_length'])


class Flat(Problem):
    '''
    Defines the Flat problem, in which all individuals receive fitness
    based on how many connection genes are connected to the input.
    The only operator in this function is 'None', meaning only
    connection genes actually evolve.
    '''
    operators = [None]
    max_arity = 2

    def __init__(self, _):
        '''
        Doesn't require initialization, but must implement.
        '''
        pass

    def get_fitness(self, individual):
        '''
        Returns the percentage of connection genes connected to the input.
        '''
        correct, total = 0, 0
        for gene in individual.genes:
            if gene is not None:
                if gene < 0:
                    correct += 1
                total += 1
        return correct / float(total)


class Active(Problem):
    '''
    Defines the Active problem, in which all individuals receive fitness
    based on how many active nodes they have.
    The only operator in this function is 'None', meaning only
    connection genes actually evolve.
    '''
    operators = [None]
    max_arity = 2

    def __init__(self, config):
        '''
        Saves configuration for use during evaluation.
        '''
        self.config = config

    def get_fitness(self, individual):
        '''
        Returns the percentage of nodes that are active.
        '''
        return len(individual.active) / float(self.config['graph_length'])

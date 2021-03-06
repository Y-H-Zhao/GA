# -*- coding: utf-8 -*-
"""
Created on Sun May 13 08:34:54 2018

@author: ZYH
"""
# -------------------------------
#
# Genetic Algorithm Optimization in TensorFlow
#
# We are going to implement a genetic algorithm
#   to optimize to a ground truth array.  The ground
#   truth will be an array of 50 floating point
#   numbers which are generated by:
#   f(x)=sin(2*pi*x/50) where 0<x<50
#
# Each individual will be an array of 50 floating
#   point numbers and the fitness will be the average
#   mean squared error from the ground truth.
#
# We will use TensorFlow's update function to run the
#   different parts of the genetic algorithm.
#
# While TensorFlow isn't really the best for GA's,
#   this example shows that we can implement different
#   procedural algorithms with TensorFlow operations.

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.python.framework import ops
ops.reset_default_graph()


# Genetic Algorithm Parameters
pop_size = 100
features = 50
selection = 0.2
mutation = 1./pop_size
generations = 200
num_parents = int(pop_size*selection)
num_children = pop_size - num_parents

# Start a graph session
#初始化计算图会话，创建ground truth函数，该函数用来计算适应度
sess = tf.Session()

# Create ground truth
truth = np.sin(2*np.pi*(np.arange(features, dtype=np.float32))/features)

# Initialize population array
#使用Tensorflow变量（随机正态分布）初始化种群
population = tf.Variable(np.random.randn(pop_size, features), dtype=tf.float32)

# Initialize placeholders
#占位符 种群个体 交叉个体 变异个体
truth_ph = tf.placeholder(tf.float32, [1, features])
crossover_mat_ph = tf.placeholder(tf.float32, [num_children, features])
mutation_val_ph = tf.placeholder(tf.float32, [num_children, features])

# Calculate fitness (MSE)
#计算种群适应度 均方误差的负值，选着适应度高的个体
fitness = -tf.reduce_mean(tf.square(tf.subtract(population, truth_ph)), 1)
top_vals, top_ind = tf.nn.top_k(fitness, k=pop_size)

# Get best fit individual
#检索适应最高的个体
best_val = tf.reduce_min(top_vals)
best_ind = tf.arg_min(top_vals, 0)
best_individual = tf.gather(population, best_ind)

# Get parents
#排序父种群，截取适应度较高的作为下一代
population_sorted = tf.gather(population, top_ind)
parents = tf.slice(population_sorted, [0, 0], [num_parents, features])


# Get offspring
# Indices to shuffle-gather parents
#在前20个数字中有放回地随机抽取80个作为子代
rand_parent1_ix = np.random.choice(num_parents, num_children)
rand_parent2_ix = np.random.choice(num_parents, num_children)
# Gather parents by shuffled indices, expand back out to pop_size too
# 交叉获取子代个体
rand_parent1 = tf.gather(parents, rand_parent1_ix)
rand_parent2 = tf.gather(parents, rand_parent2_ix)
rand_parent1_sel = tf.multiply(rand_parent1, crossover_mat_ph)
rand_parent2_sel = tf.multiply(rand_parent2, tf.subtract(1., crossover_mat_ph))
children_after_sel = tf.add(rand_parent1_sel, rand_parent2_sel)

# Mutate Children
mutated_children = tf.add(children_after_sel, mutation_val_ph)

# Combine children and parents into new population
# 结合子代和父代组成新的种群
new_population = tf.concat(axis=0, values=[parents, mutated_children])
# 新种群变成现在种群 下面使用run方法进行循环
step = tf.group(population.assign(new_population))

init = tf.global_variables_initializer()
sess.run(init)

# Run through generations
for i in range(generations):
    # Create cross-over matrices for plugging in.
    # 创建随机交叉矩阵
    crossover_mat = np.ones(shape=[num_children, features])
    crossover_point = np.random.choice(np.arange(1, features-1, step=1), num_children)
    for pop_ix in range(num_children):
        crossover_mat[pop_ix,0:crossover_point[pop_ix]]=0.
    # Generate mutation probability matrices
    # 创建随机变异矩阵
    mutation_prob_mat = np.random.uniform(size=[num_children, features])
    mutation_values = np.random.normal(size=[num_children, features])
    mutation_values[mutation_prob_mat >= mutation] = 0
    
    # Run GA step
    feed_dict = {truth_ph: truth.reshape([1, features]),
                 crossover_mat_ph: crossover_mat,
                 mutation_val_ph: mutation_values}
    step.run(feed_dict, session=sess)
    best_individual_val = sess.run(best_individual, feed_dict=feed_dict)
    
    if i % 5 == 0:
       best_fit = sess.run(best_val, feed_dict = feed_dict)
       print('Generation: {}, Best Fitness (lowest MSE): {:.2}'.format(i, -best_fit))

plt.plot(truth, label="True Values")
plt.plot(np.squeeze(best_individual_val), label="Best Individual")
plt.axis((0, features, -1.25, 1.25))
plt.legend(loc='upper right')
plt.show()

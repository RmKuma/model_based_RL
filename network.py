from keras.layers import Lambda, Input, Dense, BatchNormalization, ReLU, Concatenate
from keras.models import Model
from keras.optimizers import Adam
from keras.regularizers import l2
from keras.activations import tanh
from keras.datasets import mnist
from keras.losses import mse, binary_crossentropy
from keras.utils import plot_model
from keras import backend as K

import numpy as np
import tensorflow as tf

class Network(object):
    def __init__(self, layer_structure, action_shape, state_shape, output_shape, loss='mse', metrics=None):
        self.action_shape = action_shape
        self.state_shape = state_shape
        self.output_shape = output_shape

        self.network = self.build_network(layer_structure)
        self.network_compile(loss, Adam(learning_rate=0.001), metrics)

    def network_compile(self, loss, optimizer, metrics):
        if metrics is None:
            self.network.compile(loss=loss, optimizer=optimizer)
        else:
            self.network.compile(loss=loss, optimizer=optimizer, metrics=[metrics])

    def build_network(self, layer_structure):
        actions_input = Input(shape=(self.action_shape, ), name='action_input')
        actions = Dense(32, activation='relu')(actions_input)
        actions = BatchNormalization()(actions)
        actions = ReLU()(actions)
        states_input = Input(shape=(self.state_shape, ), name='state_input')
        states = Dense(32, activation='relu', kernel_initializer='orthogonal', kernel_regularizer=l2(0.01))(states_input)
        states = BatchNormalization()(states)
        x = Concatenate()([actions, states])
        x = Dense(64, activation='relu', kernel_initializer='orthogonal', kernel_regularizer=l2(0.01))(x)
        for dims in layer_structure:
            x = Dense(dims, kernel_initializer='orthogonal', kernel_regularizer=l2(0.01))(x)
            x = BatchNormalization()(x)
            x = ReLU()(x)
        output = Dense(self.output_shape)(x)
        outputs = Model([actions_input, states_input], output, name='model')
        return outputs

    def train(self, state_data, action_data, output_data, training_epochs):
        action_data = np.array(action_data).reshape([-1, self.action_shape])
        state_data = np.array(state_data).reshape([-1, self.state_shape])
        output_data = np.array(output_data).reshape([-1, self.output_shape])
        self.network.fit([action_data, state_data], output_data, nb_epoch=training_epochs, batch_size=1024, verbose=0)
        return

    def predict(self, state_data, action_data):
        action_data = np.array(action_data).reshape([-1, self.action_shape])
        state_data = np.array(state_data).reshape([-1, self.state_shape])
        input_data = [action_data, state_data]
        return self.network.predict(input_data)

    def save(self, save_path):
        pass

    def load(self, load_path):
        pass

class DoneNetwork(Network):
    def __init__(self, layer_structure, action_shape, state_shape, output_shape,
                 loss='binary_crossentropy', metrics='accuracy'):
        super().__init__(layer_structure, action_shape, state_shape, output_shape, loss, metrics)

    def build_network(self, layer_structure):
        actions_input = Input(shape=(self.action_shape, ), name='action_input')
        actions = Dense(32, activation='relu')(actions_input)
        actions = BatchNormalization()(actions)
        actions = ReLU()(actions)
        states_input = Input(shape=(self.state_shape, ), name='state_input')
        states = Dense(32, activation='relu', kernel_initializer='orthogonal', kernel_regularizer=l2(0.01))(states_input)
        states = BatchNormalization()(states)
        x = Concatenate()([actions, states])
        x = Dense(64, activation='tanh', kernel_initializer='orthogonal', kernel_regularizer=l2(0.01))(x)
        for dims in layer_structure:
            x = Dense(dims, kernel_initializer='orthogonal', kernel_regularizer=l2(0.01))(x)
            x = BatchNormalization()(x)
            x = Dense(dims, activation='tanh', kernel_initializer='orthogonal', kernel_regularizer=l2(0.01))(x)
        output = Dense(self.output_shape, activation='sigmoid')(x)
        outputs = Model([actions_input, states_input], output, name='model')
        return outputs

    def train(self, state_data, action_data, output_data, training_epochs):
        action_data = np.array(action_data).reshape([-1, self.action_shape])
        state_data = np.array(state_data).reshape([-1, self.state_shape])
        output_data = np.array(output_data)
        self.network.fit([action_data, state_data], output_data, nb_epoch=training_epochs, batch_size=256, verbose=1)
        return

    def predict(self, state_data, action_data):
        action_data = np.array(action_data).reshape([-1, self.action_shape])
        state_data = np.array(state_data).reshape([-1, self.state_shape])
        input_data = [action_data, state_data]
        return self.network.predict(input_data)

from acoustic_model import AcousticModel

from tensorflow import keras

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import ModelCheckpoint
from datetime import datetime
from tensorflow.keras import regularizers
from tensorflow.keras.constraints import MaxNorm


class CNN_model(AcousticModel):

    # NOTE: REMOVE THIS PART?
    # num_epochs = 10 #72 500
    # num_batch_size = 32
    # num_channels = 1
    num_labels = 2

    def __init__(self, *args):
        """Class init
        Parameters
        ----------
        args[0]: int
            Number of rows
        args[1]: int
            Number of columns
        args[2]: int
            Number of channels
        args[3]: bool
            Indicates if the number-of-channels is the first input or not
        """
        super(CNN_model, self).__init__()

        self.predicts = None
        if len(args) > 0:
            self.num_rows = args[0]
            self.num_columns = args[1]
            self.num_channels = args[2]
            self.channel_first = args[3]

    def _make_cnn_model(self, init_mode, dropout_rate, weight_constraint):
        """Make a CNN model"""
        if self.channel_first:
            keras.backend.set_image_data_format("channels_first")
            input_shape = (self.num_channels, self.num_rows, self.num_columns)
            data_format = "channels_first"
        else:
            input_shape = (self.num_rows, self.num_columns, self.num_channels)
            data_format = "channels_last"

        self.acoustic_model = Sequential()
        self.acoustic_model.add(
            Conv2D(
                filters=64,
                kernel_size=3,
                input_shape=input_shape,
                activation="relu",
                data_format=data_format,
                padding="same",
                kernel_regularizer=regularizers.l2(l=0.01),
                kernel_initializer=init_mode,
                kernel_constraint=MaxNorm(weight_constraint),
            )
        )

        self.acoustic_model.add(
            Conv2D(
                filters=64,
                kernel_size=3,
                activation="relu",
                kernel_regularizer=regularizers.l2(l=0.01),
                kernel_initializer=init_mode,
                kernel_constraint=MaxNorm(weight_constraint),
            )
        )

        self.acoustic_model.add(Dropout(dropout_rate))
        self.acoustic_model.add(MaxPooling2D(pool_size=2))
        self.acoustic_model.add(Flatten())
        self.acoustic_model.add(
            Dense(
                100,
                activation="relu",
                kernel_regularizer=regularizers.l2(l=0.01),
                kernel_initializer=init_mode,
                kernel_constraint=MaxNorm(weight_constraint),
            )
        )
        self.acoustic_model.add(Dropout(dropout_rate))
        self.acoustic_model.add(
            Dense(self.num_labels, activation="softmax", kernel_initializer=init_mode)
        )

    # NOTE: REMOVE THIS PART?
    # def _compile(self):
    #     # Compile the model
    #     self.acoustic_model.compile(loss='categorical_crossentropy',
    #                                 metrics=[Recall()],
    #                                 optimizer='adam')
    # # 'accuracy'
    #
    #     # Display model architecture summary
    #     self.acoustic_model.summary()

    def _train(self, X_train, y_train, X_test, y_test, file_path, epochs, batch_size):
        """Train a CNN model
        Parameters
        ----------
        file_path: str
                file path to save the trained model
        """
        checkpointer = ModelCheckpoint(
            filepath=file_path
            + "_weights.best.cnn.hdf5",  # 'saved_models/weights.best.basic_cnn.hdf5'
            verbose=1,
            save_best_only=True,
        )
        start = datetime.now()

        print("self.acoustic_model", self.acoustic_model)

        weights = {0: 1 / y_train[:, 0].mean(), 1: 1 / y_train[:, 1].mean()}
        history = self.acoustic_model.fit(
            X_train,
            y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(X_test, y_test),
            shuffle=True,
            class_weight=weights,
            callbacks=[checkpointer],
            verbose=1,
        )
        self.plot_measures(history, file_path)
        duration = datetime.now() - start
        print("Training completed in time: ", duration)

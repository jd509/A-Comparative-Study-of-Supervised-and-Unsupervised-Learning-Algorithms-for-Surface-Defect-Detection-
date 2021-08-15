#importing modules
import os, sys, threading
from pathlib import Path

#import GUI modules
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QObject, QRunnable, QSize, QThread, QThreadPool, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QWidget, QMessageBox, QProgressDialog
from numpy.core.fromnumeric import around
from train_machine_learning_models import Train


class UserInterface(QWidget):
    def __init__(self):
        super(UserInterface, self).__init__()
        self.ui_file_path = os.path.dirname(os.getcwd()) + '/resource/user_interface.ui'
        self.ui = uic.loadUi(self.ui_file_path, self)

        self.dataset_folder_path = ''
        self.glcm_feature_extraction_complete = False
        self.lbglcm_feature_extraction_complete = False

        # Button Connections
        self.ui.browse_btn.clicked[bool].connect(self.browse_dataset_path)
        self.ui.extract_glcm_features_btn.clicked[bool].connect(self.extract_glcm_features)
        self.ui.extract_lbglcm_features_btn.clicked[bool].connect(self.extract_lbglcm_features)
        self.ui.train_rf_model_btn.clicked[bool].connect(self.train_random_forest_model)
        self.ui.train_xtra_trees_model_btn.clicked[bool].connect(self.train_xtra_trees_model)
        self.ui.train_gradient_boosting_model_btn.clicked[bool].connect(self.train_gradient_boosting_model)
        self.ui.train_cnn_model_btn.clicked[bool].connect(self.train_convolutional_neural_network_model)
        self.ui.display_training_accuracy_btn.clicked[bool].connect(self.display_training_accuracy)

        self.show()

    def browse_dataset_path(self):
        self.dataset_folder_path = str(QFileDialog.getExistingDirectory())
        self.ui.dataset_location_txtbox.setText(self.dataset_folder_path)
        self.model_training_obj = Train(self.dataset_folder_path)
        print(self.model_training_obj.dataset_directory)
        self.ui.status_textbox.setText('Loaded Dataset!')

    def extract_glcm_features(self):
        try:
            self.glcm_pixel_pair_angle = int(self.ui.pixel_angle_glcm_txtbox.text())
            self.glcm_pixel_distance = float(self.ui.pixel_distance_glcm_txtbox.text())
        except ValueError:
            prompt = QtWidgets.QMessageBox()
            prompt.setWindowTitle("Input Error")
            prompt.setText("Please enter a float value for pixel distance and integer for pair angle for in the text box")
            prompt.setIcon(QtWidgets.QMessageBox.Critical)
            ret = prompt.exec_()
        else:
            self.model_training_obj.extract_features_using_glcm(dist=self.glcm_pixel_distance, 
                                                                angle=self.glcm_pixel_pair_angle)
            self.model_training_obj.prepare_dataset_for_supervised_learning(self.model_training_obj.glcm_image_features, 0.25, "GLCM")
            self.ui.status_textbox.setText('GLCM features computed!')

    def extract_lbglcm_features(self):
        try:
            self.lbglcm_pixel_pair_angle = int(self.ui.pixel_angle_lbglcm_txtbox.text())
            self.lbglcm_pixel_distance = float(self.ui.pixel_distance_lbglcm_txtbox.text())
            self.lbglcm_radius_of_neighbors = float(self.ui.radiu_of_neighbors_lbglcm_txtbox.text())
        except ValueError:
            prompt = QtWidgets.QMessageBox()
            prompt.setWindowTitle("Input Error")
            prompt.setText("Please enter an int value for pixel pair angle and floating point values for others")
            prompt.setIcon(QtWidgets.QMessageBox.Critical)
            ret = prompt.exec_()
        else:
            self.model_training_obj.extract_features_using_lbglcm(dist = self.lbglcm_pixel_distance, 
                                                                angle=self.lbglcm_pixel_pair_angle, 
                                                                radius_of_neighbors=self.lbglcm_radius_of_neighbors)
            self.model_training_obj.prepare_dataset_for_supervised_learning(self.model_training_obj.lbglcm_image_features, 0.25, "LBGLCM")
            self.ui.status_textbox.setText('LBGLCM features computed!')

    def train_random_forest_model(self):
        try:
            self.number_of_trees_rf_model = int(self.ui.num_trees_train_rf_txtbox.text())
            self.maximum_features_selected_rf = str(self.ui.max_features_train_rf_cmbox.currentText())
        except ValueError:
            prompt = QtWidgets.QMessageBox()
            prompt.setWindowTitle("Input Error")
            prompt.setText("Please enter an int value for number of trees")
            prompt.setIcon(QtWidgets.QMessageBox.Critical)
            ret = prompt.exec_()
        else:
            self.model_training_obj.train_random_forest_classifier(self.number_of_trees_rf_model, self.maximum_features_selected_rf,1,1500,-1)
            # self.random_forest_training_thread = threading.Thread(target=self.model_training_obj.train_random_forest_classifier, 
            #                                                 kwargs={'number_of_trees':self.number_of_trees_rf_model, 
            #                                                   'max_features_to_classify':self.maximum_features_selected_rf})
            self.ui.status_textbox.setText('Random Forest model trained!')
    
    def train_xtra_trees_model(self):
        try:
            self.number_of_trees_xtra_trees_model = int(self.ui.num_trees_xtra_trees_txtbox.text())
            self.maximum_features_selected_xtra_trees = str(self.ui.max_features_train_xtra_trees_cmbox.currentText())
        except ValueError:
            prompt = QtWidgets.QMessageBox()
            prompt.setWindowTitle("Input Error")
            prompt.setText("Please enter an int value for number of trees")
            prompt.setIcon(QtWidgets.QMessageBox.Critical)
            ret = prompt.exec_()
        else:
            self.model_training_obj.train_xtra_trees_classifier(self.number_of_trees_xtra_trees_model, self.maximum_features_selected_xtra_trees, 1, 1500, -1)
            print(self.model_training_obj.model_accuracies['xtra_trees_glcm'])
            print(self.model_training_obj.model_accuracies['xtra_trees_lbglcm'])
            # self.extra_trees_training_thread = threading.Thread(target=self.model_training_obj.train_xtra_trees_classifier, 
            #                                                 kwargs={'number_of_trees':self.number_of_trees_xtra_trees_mode, 
            #                                                       'max_features_to_classify':self.maximum_features_selected_xtra_trees})
            self.ui.status_textbox.setText('Extra Trees model trained!')

    def train_gradient_boosting_model(self):
        try:
            self.num_estimators_train_gb_model = int(self.ui.num_estimators_train_gb_txtbox.text())
            self.max_features_train_gb_model = str(self.ui.max_features_train_gb_cmbox.currentText())
            self.learning_rate_train_gb_model = float(self.ui.learning_rate_train_gb_txtbox.text())
        except ValueError:
            prompt = QtWidgets.QMessageBox()
            prompt.setWindowTitle("Input Error")
            prompt.setText("Please enter an int value for number of estimators and float value for learning rate")
            prompt.setIcon(QtWidgets.QMessageBox.Critical)
            ret = prompt.exec_()
        else:
            self.model_training_obj.train_gradient_boosting_classifier(self.num_estimators_train_gb_model, self.max_features_train_gb_model, 'deviance', 0.2, 1500)
            print(self.model_training_obj.model_accuracies['gradient_boosting_glcm'])
            print(self.model_training_obj.model_accuracies['gradient_boosting_lbglcm'])
            # self.gradient_boosting_thread = threading.Thread(target=self.model_training_obj.train_gradient_boosting_classifier, 
            #                                                 kwargs={'number_of_trees':self.num_estimators_train_gb_model, 
            #                                                       'max_features_to_classify':self.max_features_train_gb_model})
            self.ui.status_textbox.setText('Gradient Boosting model trained!')
    
    def train_convolutional_neural_network_model(self):
        cnn_checkpoint_file = Path(os.path.dirname(os.getcwd()) + '/' + 'trained_cnn_model.ckpt')
        try:
            self.epochs_for_training = int(self.ui.num_epochs_train_cnn_txtbox.text())
            self.validation_split_train_cnn = float(self.ui.validation_split_train_cnn_txtbox.text())
        except ValueError:
            if not self.ui.pretrained_model_chckbox.isChecked() and cnn_checkpoint_file.exists():
                prompt = QtWidgets.QMessageBox()
                prompt.setWindowTitle("Input Error")
                prompt.setText("Please enter an int value for epochs and float value for validation split")
                prompt.setIcon(QtWidgets.QMessageBox.Critical)
                ret = prompt.exec_()
        if not self.ui.pretrained_model_chckbox.isChecked():
            # self.cnn_thread = threading.Thread(target=self.model_training_obj.CNN, 
            #                                                 kwargs={'epoch':self.epochs_for_training, 
            #                                                       'val_split':self.validation_split_train_cnn,
            #                                                       'save_model': True})
            self.model_training_obj.CNN(self.epochs_for_training, self.validation_split_train_cnn, True)
            self.ui.status_textbox.setText('CNN model trained!')
        else:
            # self.cnn_thread = threading.Thread(target=self.model_training_obj.pretrained_CNN, 
            #                                                 kwargs={'validation_split':self.validation_split_train_cnn})
            self.model_training_obj.pretrained_CNN(self.validation_split_train_cnn)
            self.ui.status_textbox.setText('Using pretrained CNN model')
    

    def display_training_accuracy(self):
        self.ui.window_change_stack_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = UserInterface()
    sys.exit(app.exec())


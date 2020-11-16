import sys
import json

import numpy
import pygad

import pyqtgraph as pg
import pyqtgraph.exporters
import random

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.Qt import Qt
from PyQt5.QtCore import QEvent, Signal
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsItem, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QPen, QBrush, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

qtcreator_file  = "untitled.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

STOPSIM = False
generations = []
universeFitness = []
genFitness = []
universe = []
last_fitness = 0
function_inputs = [4,-2,3.5,5,-11,-4.7] # Function inputs.
desired_output = 44 # Function output.

class Rectangle(QGraphicsRectItem):
    window = 0
    chromosome = []
    fitness = 0
    itemDoubleClicked = Signal(object)

    def mouseDoubleClickEvent(self, event):
      self.window.chosenChromosome.setText(str(self.chromosome))
      self.window.chosenFitness.setText(str(self.fitness))

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.runButton.clicked.connect(self.play)
        self.loadfitnessButton.clicked.connect(self.loadfitness)
        self.exportfitnessplotButton.clicked.connect(self.exportFitnessPlot)
        self.stopButton.clicked.connect(self.stopSimulation)
        self.exportlogButton.clicked.connect(self.exportLog)
        self.universeSlider.valueChanged.connect(self.updateUniverseGen)
        #self.universePlot.mousePressEvent(QMouseEvent(QEvent.MouseButtonPress, QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier))
        #print(dir(self.universePlot))

    def updateUniverseGen(self):
      global universe
      global universeFitness
      self.universeGen.setText(str(self.universeSlider.value()))

      population = universe[int(self.universeGen.text())]
      print("POP: ", population)

      scene = QtWidgets.QGraphicsScene(self.universePlot)
      #Without setSceneRect, the rectangle position will be considered as the 0,0,
      # and the whole scene rotates around it, instead of the rectangle moving.
      scene.setSceneRect(0,0,100,100)

      self.universePlot.setScene(scene)
      for i, elem in enumerate(population):
        x = random.randint(0,200)
        y = random.randint(0,200)
        rect = Rectangle(float(0),float(0),float(40),float(40))
        print(dir(rect))
        rect.setPos(x,y)
        rect.setFlag(QGraphicsItem.ItemIsMovable)
        #rect.mouseDoubleClickEvent(self.showDetails)
        rect.chromosome = population[i]
        rect.window = self
        print(universeFitness[int(self.universeGen.text())])
        rect.fitness = universeFitness[int(self.universeGen.text())][i]
        scene.addItem(rect)
        QtGui.QApplication.processEvents()

    def exportLog(self):
      log = self.simulationLog.toPlainText()
      file_path = QtWidgets.QFileDialog().getSaveFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)")

      print(file_path)

      if file_path:
        with open(file_path[0], 'w') as f:
          f.write(log)


    def stopSimulation(self):
      global generations
      global genFitness
      global STOPSIM
      global universe
      universe = []
      generations = []
      genFitness = []
      STOPSIM = True

    def exportFitnessPlot(self):
      exporter = pg.exporters.ImageExporter(self.fitnessPlot.plotItem)
      #exporter.parameters()['width'] = 100   # (note this also affects height parameter)

      file_path = QtWidgets.QFileDialog().getSaveFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)")

      if file_path:
          exporter.export(file_path[0])

    def loadfitness(self):
      dlg = QFileDialog()
      dlg.setFileMode(QFileDialog.AnyFile)
      options = QFileDialog.Options()
      options |= QFileDialog.DontUseNativeDialog
      fileName, _ = dlg.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
      if fileName:
        with open(fileName) as json_file:
          data = json.load(json_file)
          self.generationsField.setText(str(data["generations"]))
          self.numparentsField.setText(str(data["parents"]))
          self.populationField.setText(str(data["population"]))
          self.numgenesField.setText(str(data["numgene"]))
          self.percmutgeneField.setText(str(data["percentmutgene"]))
          self.pmutField.setText(str(data["pmut"]))
          self.pcrossField.setText(str(data["pcross"]))
          #self.universeSlider.setTickInterval(data["generations"])
          self.universeSlider.setMaximum(data["generations"])

    def play(self):
      global generations
      global genFitness
      global STOPSIM
      generations = []
      genFitness = []
      if self.clearFitnessplotCheckbox.isChecked():
        self.fitnessPlot.clear()
      global function_inputs
      global desired_output
      def fitness_func(solution, solution_idx):
        global function_inputs
        global desired_output
        output = numpy.sum(solution*function_inputs)
        fitness = 1.0 / numpy.abs(output - desired_output)
        return fitness
      def callback_generation(ga_instance):
       global STOPSIM
       print("gen")
       global last_fitness
       print("Generation = {generation}".format(generation=ga_instance.generations_completed))
       print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
       print("Change     = {change}".format(change=ga_instance.best_solution()[1] - last_fitness))
       print("-----------------------------------------------------")
       global generations
       global universeFitness
       global genFitness
       universeFitness.append(ga_instance.cal_pop_fitness())
       universe.append(ga_instance.population)
       generations.append(len(generations))
       genFitness.append(ga_instance.best_solution()[1])
       #plotgen(self)
       self.fitnessPlot.plot(generations, genFitness)
       self.simulationLog.append("Generation = {generation}".format(generation=ga_instance.generations_completed))
       self.simulationLog.append("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))
       self.simulationLog.append("Change     = {change}".format(change=ga_instance.best_solution()[1] - last_fitness))
       self.simulationLog.append("-----------------------------------------------------")
       QtGui.QApplication.processEvents()
       if STOPSIM == True:
         return "stop"

      keep_parents = 7
      init_range_low = -2
      init_range_high = 5
      num_generations = int(self.generationsField.text())
      num_parents_mating = int(self.numparentsField.text())
      sol_per_pop = int(self.populationField.text())
      crossover_type = self.crossoverCombo.currentText()
      if crossover_type == "Single Point":
        crossover_type = "single_point"
      mutation_type = self.mutationCombo.currentText()
      if mutation_type == "Random":
        mutation_type = "random"
      num_genes = int(self.numgenesField.text())
      mutation_percent_genes = int(self.percmutgeneField.text())
      parent_selection_type = "sss"
      ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating, 
                       fitness_func=fitness_func,
                       sol_per_pop=sol_per_pop, 
                       num_genes=num_genes,
                       init_range_low=init_range_low,
                       init_range_high=init_range_high,
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       crossover_type=crossover_type,
                       mutation_type=mutation_type,
                       mutation_percent_genes=mutation_percent_genes,
                       on_generation=callback_generation)

      ga_instance.run()
      print(universe)
      print(dir(ga_instance))
      #print(generations)
      #print(genFitness)

      # Returning the details of the best solution.
      solution, solution_fitness, solution_idx = ga_instance.best_solution()
      print("Parameters of the best solution : {solution}".format(solution=solution))
      print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
      print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

      prediction = numpy.sum(numpy.array(function_inputs)*solution)
      print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))

      if ga_instance.best_solution_generation != -1:
        print("Best fitness value reached after {best_solution_generation} generations.".format(best_solution_generation=ga_instance.best_solution_generation))

      STOPSIM = False
      print(num_generations)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

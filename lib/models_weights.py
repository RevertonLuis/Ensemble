import numpy
import random

def compute_models_weights_from_members(settings):

    """ Subroutine that computes the weight of each model from it's number of members """

    # Dictionary with the models, not the members, example:
    # GEP06 is a member of the GEFS model
    models = {}

    for model in settings["models"]:
        if  settings["model_%s" % model][0] in models.keys():
            models[settings["model_%s" % model][0]] += 1
        else:
            models[settings["model_%s" % model][0]] = 1

    for model in settings["models"]:
        if "automatic_weight_%s" % model in settings.keys():
            if settings["automatic_weight_%s" % model][0].lower() == "yes":
                settings["weight_%s" % model] = [1./models[settings["model_%s" % model][0]]]
        else:
            print("")
            print("Warning: automatic weight for model %s not configured" % model)
            print("The weight configured in the settings (peso_%s = %s) will be used" % (model, settings["peso_%s" % model][0]))
            print("Add the automatic_weight_%s Yes/No in the settings.txt file" % model)
            print("")



def compute_models_weights_matrices(models, target_grid):

    """ Subroutine that will computes the models weights matrices """

    for m in models.ensemble_data.keys():
        for r in models.ensemble_data[m].keys():

            # There might be cases where the run from the same
            # model have different grid resolution, like when the WRF model changed
            # from the ensemble_9k to SSEOP...
            # So, for each model and run build a new weight matrix
            weight_matrix = numpy.ones(target_grid.lat.shape, 'f')

            # Computes the weight matrix

            # Update the model.ensemble_data with the weight matrix
            models.ensemble_data[m][r].update({"weight_matrix": weight_matrix})


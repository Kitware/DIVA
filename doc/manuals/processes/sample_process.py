from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess

class ClassifierProcess(KwiverProcess):
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)

        # declare configuration
        self.add_config_trait("model_file", "model_file",
                                'dummy.model', 'Model file for the classifier')
        self.declare_config_using_trait('model_file')

        # set up flags
        required = process.PortFlags()
        required.add(self.flag_required)
        optional = process.PortFlags()
        
        # declare ports
        self.declare_input_port_using_trait('image', required)
        self.declare_input_port_using_trait('file_name', optional )
        self.declare_output_port_using_trait( 'double_vector', required );

    def _configure(self):
        # Configure the process
        self.classifier = Classifier(self.config_value("model_file"))

    def _step(self):
        # Step Function for the process
        img_container = self.grab_input_using_trait('image')
        video_name = self.grab_input_using_trait('file_name')
        # Classify the image
        class_score = self.classifier.classify(img_container.image())
        # Push results to port
        self.push_to_port_using_trait('double_vector', class_score)



def __sprokit_register__():
    from sprokit.pipeline import process_factory
    module_name = 'python:kwiver.ClassifierSample'
    if process_factory.is_process_module_loaded(module_name):
        return
    process_factory.add_process('ClassifierSample', 'Dummy Classifier', 
                                ClassifierProcess)
    process_factory.mark_process_module_as_loaded(module_name)

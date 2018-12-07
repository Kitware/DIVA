#ifndef CLASSIFIER_PROCESS_H
#define CLASSIFIER_PROCESS_H
#include <sprokit/pipeline/process.h>
#include <processes/optical_flow/diva_classifier_process_export.h>
#include <vital/vital_types.h>

namespace diva {

create_config_trait( model_file, vital::path_t, "dummy.model",
                "Model file for the classifier" );
class DIVA_CLASSIFIER_PROCESSES_NO_EXPORT classifier_process
  : public sprokit::process
{
public:
  classifier_process( kwiver::vital::config_block_sptr const& config ) 
      : process( config )
      : d( new classifier_process::priv )
  {
  
    declare_config_using_trait( model_file );
    // Set up flags
    sprokit::process::port_flags_t optional;
    sprokit::process::port_flags_t required;
    required.insert( flag_required );

    // Declare input ports
    declare_input_port_using_trait( image, required );
    declare_input_port_using_trait( file_name, optional );

    declare_output_port_using_trait( double_vector, required );
  }
protected:
  void _configure()
  {
    scoped_configure_instrumentation();
    d->classifer = ClassifierModel(config_value_using_trait( model_file ); 
  }

  void _step()
  {
    auto image_container = grab_from_port_using_trait( image );
    auto file_name = grab_from_port_using_trait( file_name ); 
    std::vector<double> output_classes = d->classifier.classify( image_container->get_image() );
    push_to_port_using_trait( output_classes );
  }

private:
  class priv
  {
    
  };
  const std::unique_ptr<priv> d;
}; // end class classifier_process

}  // end namespace

#endif // CLASSIFIER_PROCESS_H

# nf-core Pipeline Compliance Report

**Pipeline:** `aquascope`

**Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope`

**Date:** 2025-04-29 01:09:49

**nf-core Validator Version:** 0.1.0


## Summary

- **Components Analyzed:** 51

- **Requirements Checked:** 569

- **Passed Requirements:** 421

- **Failed Requirements:** 148

- **Compliance Score:** 73.99%


## Component Type Breakdown

| Component Type | Count | Avg. Compliance |

|---------------|-------|----------------|

| other_file | 6 | 34.83% |

| module | 18 | 86.26% |

| workflow | 3 | 45.33% |

| subworkflow | 9 | 61.26% |

| main_workflow | 1 | 76.92% |

| nextflow_config | 1 | 77.00% |

| schema_file | 1 | 50.00% |

| documentation_file | 4 | 51.42% |

| config_file | 8 | 77.92% |



## Top Violations

- **environment_yml:** 6 occurrences

  - *Description:* Module should have an accompanying environment.yml file

  - *Example fix:* Create an environment.yml file in the same directory with conda dependencies: 'name: kraken2_db_preparation
channels:
  - conda-forge
  - defaults
dependencies:
  - conda-forge::sed=4.7'



- **5.2:** 5 occurrences

  - *Description:* Meta.yml documentation of channel structure

  - *Example fix:* Create a meta.yml file for the subworkflow that describes the input and output channel structures.



- **module_documentation:** 4 occurrences

  - *Description:* Module should have documentation comments

  - *Example fix:* Add documentation comments at the top of the file explaining the purpose, inputs, outputs, and any special considerations for this module



- **documentation:** 3 occurrences

  - *Description:* Subworkflow should have documentation comments explaining its purpose and usage

  - *Example fix:* Add a comment block at the top of the file explaining the purpose of the subworkflow, its inputs, outputs, and any other relevant information



- **test_files:** 3 occurrences

  - *Description:* Module should have test files (main.nf.test and nextflow.config)

  - *Example fix:* Create test files for the module: main.nf.test and nextflow.config in a tests/ directory to ensure the module can be properly tested.



- **5.1:** 3 occurrences

  - *Description:* Code comment of channel structure

  - *Example fix:* Add comments describing the structure of input channels. For example: 'bam // channel: [mandatory] meta, bam', 'val_saverejects // boolean: [mandatory]', etc.



- **6.8:** 3 occurrences

  - *Description:* Configuration for nf-tests

  - *Example fix:* Create a nextflow.config file for testing the subworkflow that supplies ext.args to the modules.



- **file_location:** 2 occurrences

  - *Description:* Utility functions should be in the lib directory

  - *Example fix:* Move this file to the lib directory of your pipeline, e.g., lib/NfcoreTemplate.groovy or lib/Utils.groovy



- **meta_map:** 2 occurrences

  - *Description:* Input should include meta map for sample metadata

  - *Example fix:* Change input to include meta map: 'tuple val(meta), path(db)'



- **meta_yml:** 2 occurrences

  - *Description:* Module should have a meta.yml file describing inputs and outputs

  - *Example fix:* Create a meta.yml file in the same directory as main.nf that describes the module, its inputs, outputs, and authors. Include detailed descriptions of input/output channel structures.



## Component Details

### Config_File Components

#### modules.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/modules.config`

- **Compliance Score:** 55.56%

- **Passed:** 5 requirements

- **Failed:** 4 requirements


##### Failed Requirements

- ❌ **ext_args_format:** ext.args should be defined as closures when appropriate

  - **Fix:** Convert simple string ext.args to closures for proper evaluation. For example, change 'ext.args = '--quiet'' to 'ext.args = { '--quiet' }' and change array-joined ext.args to proper closures that return joined strings.

- ❌ **consistent_formatting:** Config should have consistent formatting and indentation

  - **Fix:** Fix inconsistent indentation throughout the file. Some blocks use tabs while others use spaces. Standardize on spaces for indentation.

- ❌ **pattern_consistency:** File patterns should be consistent

  - **Fix:** Fix inconsistent pattern formats. For example, in 'MINIMAP2_ALIGN_LONG', the pattern is '*.{bam,.bai}' which has an incorrect comma before .bai, while other modules use '*.{bam,bai}'

- ❌ **mode_consistency:** publishDir mode should be consistent

  - **Fix:** Some modules use hardcoded mode values like 'mode: "copy"' while others use 'mode: params.publish_dir_mode'. Standardize to use params.publish_dir_mode throughout.


##### Passed Requirements

- ✅ **config_structure:** Config file should have appropriate structure and organization

- ✅ **publishdir_format:** publishDir should be properly formatted

- ✅ **module_naming:** Module names should follow nf-core conventions

- ✅ **multi_command_piping:** Multi-command piping should be avoided unless necessary

- ✅ **parameter_documentation:** Parameters should be well-documented



#### test_bam.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/test_bam.config`

- **Compliance Score:** 62.5%

- **Passed:** 5 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **test_data_reference:** Test data should be referenced using modules_testdata_base_path parameter

  - **Fix:** Replace direct paths to test data with references using params.modules_testdata_base_path. For example, replace '${projectDir}/assets/references/SARS-CoV-2.reference.fasta' with references to the nf-core test datasets repository.

- ❌ **typo_in_path:** Paths should be correctly specified without typos

  - **Fix:** Fix the typo in the gff3 path: '${projectDir}/assests/references/SARS-CoV-2.reference.gff3' should be '${projectDir}/assets/references/SARS-CoV-2.reference.gff3'

- ❌ **test_data_reuse:** Test configs should reuse existing test data when possible

  - **Fix:** Instead of using custom test data in the assets directory, use existing SARS-CoV-2 test data from the nf-core test datasets repository where possible.


##### Passed Requirements

- ✅ **config_naming:** Config file should have a clear, descriptive name

- ✅ **config_header:** Config file should have a clear header comment explaining its purpose

- ✅ **config_profile_description:** Test config should have config_profile_name and config_profile_description

- ✅ **resource_limits:** Resource limits should be defined appropriately

- ✅ **config_structure:** Config file should have a clean, organized structure



#### test_iontorrent.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/test_iontorrent.config`

- **Compliance Score:** 62.5%

- **Passed:** 5 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **test_config_content:** Test config should only contain minimal settings needed for testing

  - **Fix:** The test config contains both process and params resource limits. Keep only the params.resourceLimits and remove the process.resourceLimits section to avoid duplication.

- ❌ **test_config_typos:** Config should not contain typos or errors

  - **Fix:** There's a typo in the gff3 path: 'assests' should be 'assets'

- ❌ **test_config_syntax:** Config should have valid Nextflow syntax

  - **Fix:** There's a syntax error at the end of the file - an unexpected '#' character. Remove this comment or format it properly with '//' for single line or '/*...*/' for multi-line comments.


##### Passed Requirements

- ✅ **config_header:** Config file should have a proper header with description

- ✅ **config_naming:** Config file should follow naming conventions

- ✅ **test_config_paths:** Test data paths should use projectDir for relative paths

- ✅ **test_config_profile:** Test config should have appropriate profile name and description

- ✅ **test_config_resources:** Test config should have reasonable resource limits for CI testing



#### test_illumina.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/test_illumina.config`

- **Compliance Score:** 75%

- **Passed:** 6 requirements

- **Failed:** 2 requirements


##### Failed Requirements

- ❌ **config_syntax:** Config file should have valid Nextflow syntax

  - **Fix:** Remove the '#' comment line at the end of the file and replace with proper Nextflow comment syntax using /* */ or //

- ❌ **path_validity:** All file paths should be valid and consistent

  - **Fix:** Fix the typo in the path: '${projectDir}/assests/references/SARS-CoV-2.reference.gff3' should be '${projectDir}/assets/references/SARS-CoV-2.reference.gff3'


##### Passed Requirements

- ✅ **config_naming:** Config file should have appropriate naming convention

- ✅ **config_header:** Config file should have appropriate header documentation

- ✅ **config_profile_description:** Config should include profile name and description

- ✅ **resource_definitions:** Resource definitions should be appropriate and clear

- ✅ **test_data_references:** Test data should be properly referenced

- ✅ **config_organization:** Config should be well-organized with logical grouping



#### test_ont.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/test_ont.config`

- **Compliance Score:** 77.8%

- **Passed:** 7 requirements

- **Failed:** 2 requirements


##### Failed Requirements

- ❌ **config_file_typo:** Config file should not contain typos or incorrect paths

  - **Fix:** Fix the typo in the path: 'assests' should be 'assets' in the gff3 parameter

- ❌ **config_file_syntax:** Config file should have valid Nextflow syntax

  - **Fix:** Remove the stray '# Limit code size to avoid token limits' comment at the end of the file as it's not valid Nextflow syntax


##### Passed Requirements

- ✅ **config_file_naming:** Config file should follow nf-core naming conventions

- ✅ **config_file_header:** Config file should have a proper header with description

- ✅ **config_file_structure:** Config file should have a clear structure with process and params sections

- ✅ **config_file_comments:** Config file should have appropriate comments for clarity

- ✅ **config_file_profile_name:** Test profile should have a descriptive name

- ✅ **config_file_test_data:** Test config should point to valid test data

- ✅ **config_file_resource_limits:** Resource limits should be defined appropriately



#### base.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/base.config`

- **Compliance Score:** 90%

- **Passed:** 9 requirements

- **Failed:** 1 requirements


##### Failed Requirements

- ❌ **todo_removal:** TODO comments should be addressed and removed before release

  - **Fix:** Remove the TODO comment '// TODO nf-core: Customise requirements for specific processes.' once process-specific requirements have been properly configured.


##### Passed Requirements

- ✅ **config_header:** Config file should have a proper header with pipeline name and description

- ✅ **base_config_structure:** base.config should define basic process resource requirements

- ✅ **resource_labels:** Should use standard nf-core resource labels (process_low, process_medium, etc.)

- ✅ **error_strategy:** Should have appropriate error handling strategies

- ✅ **resource_scaling:** Resources should scale with task.attempt for retry capability

- ✅ **memory_specification:** Memory should be specified in GB format

- ✅ **time_specification:** Time limits should be specified in appropriate format

- ✅ **config_organization:** Config should be well-organized and follow nf-core conventions

- ✅ **process_labels:** Should include standard process labels that match nf-core modules



#### scicomp.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/scicomp.config`

- **Compliance Score:** 100%

- **Passed:** 12 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **config_file_location:** Config file should be in the conf/ directory

- ✅ **config_file_naming:** Config file should have a descriptive name

- ✅ **config_file_header:** Config file should have a descriptive header comment

- ✅ **config_profile_description:** Config profiles should have description, contact and URL

- ✅ **config_profile_structure:** Config profiles should be properly structured

- ✅ **config_container_settings:** Container settings should be properly configured

- ✅ **config_resource_settings:** Resource settings should be properly configured

- ✅ **config_executor_settings:** Executor settings should be properly configured

- ✅ **config_file_consistency:** Config file should be consistent with nf-core style

- ✅ **config_file_documentation:** Config options should be well documented with comments

- ✅ **config_file_indentation:** Config file should use consistent indentation

- ✅ **config_file_organization:** Config file should be well-organized with logical sections



#### test.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/conf/test.config`

- **Compliance Score:** 100%

- **Passed:** 9 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **test_config_purpose:** The test.config file should define minimal test dataset to check pipeline function

- ✅ **test_config_profile:** The test.config should define a proper test profile name and description

- ✅ **test_config_input:** The test.config should define test input data

- ✅ **test_config_resources:** The test.config should define minimal resources for testing

- ✅ **test_config_genome:** The test.config should specify a genome reference if needed by the pipeline

- ✅ **test_config_path:** The test.config should be located in the conf directory

- ✅ **test_config_input_path:** Test data should use the params.pipelines_testdata_base_path variable

- ✅ **test_config_content:** The test.config should contain appropriate comments explaining its purpose and usage

- ✅ **test_config_consistency:** The test.config should be consistent with other pipeline configuration files



### Documentation_File Components

#### CHANGELOG.md

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/CHANGELOG.md`

- **Compliance Score:** 0%

- **Passed:** 0 requirements

- **Failed:** 0 requirements



#### README.md

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/README.md`

- **Compliance Score:** 45%

- **Passed:** 5 requirements

- **Failed:** 6 requirements


##### Failed Requirements

- ❌ **readme_nf_core_branding:** README should include nf-core branding and acknowledgment

  - **Fix:** Add nf-core branding and acknowledgment to the README. Include the nf-core logo and a statement acknowledging if the pipeline is based on nf-core templates or guidelines.

- ❌ **readme_installation:** README should include installation instructions

  - **Fix:** Add a section with detailed installation instructions, including prerequisites and dependencies.

- ❌ **readme_usage:** README should include basic usage examples

  - **Fix:** Add a 'Usage' section with basic command examples showing how to run the pipeline with default and custom parameters.

- ❌ **readme_parameters:** README should mention key parameters or link to parameter documentation

  - **Fix:** Add a section describing key parameters or provide a link to comprehensive parameter documentation.

- ❌ **readme_output:** README should describe pipeline outputs or link to output documentation

  - **Fix:** Add a section describing the main outputs of the pipeline or provide a link to detailed output documentation.

- ❌ **readme_license:** README should mention the license

  - **Fix:** Add a section specifying the license under which the pipeline is distributed.


##### Passed Requirements

- ✅ **readme_introduction:** README should have a clear introduction explaining the purpose of the pipeline

- ✅ **readme_badges:** README should include appropriate badges (Nextflow, conda, docker, singularity)

- ✅ **readme_documentation_link:** README should link to comprehensive documentation

- ✅ **readme_contributions:** README should include information about contributions

- ✅ **readme_citations:** README should mention citations



#### LICENSE

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/LICENSE`

- **Compliance Score:** 75%

- **Passed:** 3 requirements

- **Failed:** 1 requirements


##### Failed Requirements

- ❌ **license_year:** License should include the year of copyright

  - **Fix:** Add the year of copyright to the license, e.g., 'Copyright (c) 2023 Arun Boddapati, Matthew Hunter, ...'


##### Passed Requirements

- ✅ **license_type:** Pipelines must be open source, released with the MIT license

- ✅ **license_format:** License file should contain the standard MIT license text

- ✅ **license_copyright:** License should include appropriate copyright information



#### CITATIONS.md

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/CITATIONS.md`

- **Compliance Score:** 85.7%

- **Passed:** 6 requirements

- **Failed:** 1 requirements


##### Failed Requirements

- ❌ **pipeline_specific_citations:** Pipeline-specific tools and methods are cited

  - **Fix:** Add citations for any pipeline-specific tools, algorithms, or methods used in the aquascope pipeline. Each tool should include author, title, journal, and DOI/PMID where available.


##### Passed Requirements

- ✅ **citations_file_exists:** Pipeline has a CITATIONS.md file

- ✅ **nf_core_citation:** nf-core framework is properly cited

- ✅ **nextflow_citation:** Nextflow is properly cited

- ✅ **tools_citations:** Pipeline tools are properly cited

- ✅ **container_citations:** Software packaging/containerisation tools are properly cited

- ✅ **citation_format:** Citations follow a consistent format with proper links



### Main_Workflow Components

#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/main.nf`

- **Compliance Score:** 76.92%

- **Passed:** 10 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **main_nf_default_workflow:** The main.nf file should define a default workflow entry point

  - **Fix:** Add a workflow block named 'NFCORE_AQUASCOPE' that calls the main AQUASCOPE workflow. This should be the default entry point when the pipeline is run without specifying a workflow name.

- ❌ **main_nf_args_variable:** The args variable should be defined before being used

  - **Fix:** Define the 'args' variable before using it in the PIPELINE_INITIALISATION calls. This variable is passed to the initialization subworkflow but is not defined in the main.nf file.

- ❌ **main_nf_workflow_naming:** Workflow names should follow nf-core conventions

  - **Fix:** Rename the main workflow from 'AQUASCOPE' to 'NFCORE_AQUASCOPE' to follow nf-core naming conventions.


##### Passed Requirements

- ✅ **main_nf_dsl2:** The main.nf file should use DSL2

- ✅ **main_nf_shebang:** The main.nf file should start with the correct shebang

- ✅ **main_nf_header_comment:** The main.nf file should have a header comment with pipeline name

- ✅ **main_nf_workflow_structure:** The main.nf file should define one or more workflows

- ✅ **main_nf_pipeline_initialization:** The main.nf file should include pipeline initialization

- ✅ **main_nf_pipeline_completion:** The main.nf file should include pipeline completion

- ✅ **main_nf_workflow_organization:** Workflows should be organized in separate files and included in main.nf

- ✅ **main_nf_workflow_comments:** Each workflow should have descriptive comments

- ✅ **main_nf_code_style:** Code should follow nf-core style guidelines

- ✅ **main_nf_parameter_validation:** The main.nf file should include parameter validation



### Module Components

#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/freyja/variants/main.nf`

- **Compliance Score:** 0%

- **Passed:** 0 requirements

- **Failed:** 0 requirements



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/freyja/update/main.nf`

- **Compliance Score:** 73%

- **Passed:** 11 requirements

- **Failed:** 4 requirements


##### Failed Requirements

- ❌ **environment_yml:** An environment.yml file should exist alongside the module

  - **Fix:** Create an environment.yml file in the same directory as main.nf with the freyja package pinned to version 1.5.2, e.g.: 'name: freyja_update
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - bioconda::freyja=1.5.2'

- ❌ **meta_map:** Input channels should use meta map where appropriate

  - **Fix:** Consider using a meta map for the input channel instead of just a value. Change 'val db_name' to 'tuple val(meta), val(db_name)' for better compatibility with nf-core standards.

- ❌ **module_documentation:** Module should have documentation comments

  - **Fix:** Add documentation comments at the top of the file describing what the module does, its inputs, outputs, and any other relevant information.

- ❌ **test_files:** Module should have test files (main.nf.test and nextflow.config)

  - **Fix:** Create test files for the module: main.nf.test and nextflow.config in a tests/ directory to ensure the module can be properly tested.


##### Passed Requirements

- ✅ **module_naming:** Module name should follow the tool/subtool format

- ✅ **process_naming:** Process name should be in uppercase and match the tool/subtool format

- ✅ **label_directive:** Process should have a label directive

- ✅ **conda_directive:** Conda directive should point to environment.yml file in the module directory

- ✅ **container_directive:** Container directive should include both Singularity and Docker options

- ✅ **input_output_format:** Input and output channels should be properly defined

- ✅ **versions_output:** Module should output a versions.yml file

- ✅ **when_directive:** Module should include a when directive

- ✅ **script_section:** Script section should properly define the tool execution

- ✅ **stub_section:** Stub section should be included for testing

- ✅ **ext_args:** Module should use task.ext.args for optional arguments



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/fastp/main.nf`

- **Compliance Score:** 73%

- **Passed:** 11 requirements

- **Failed:** 4 requirements


##### Failed Requirements

- ❌ **versions_yml_format:** versions.yml should be properly formatted with correct tool name and version

  - **Fix:** The versions.yml output is missing the 'END_VERSIONS' tag at the end. Change 'END' to 'END_VERSIONS' in the cat command.

- ❌ **environment_yml:** Module should have an environment.yml file in the same directory

  - **Fix:** Create an environment.yml file in the same directory as main.nf with the fastp package pinned to version 0.23.4 (e.g., 'bioconda::fastp=0.23.4').

- ❌ **test_files:** Module should have test files (main.nf.test and nextflow.config)

  - **Fix:** Create test files main.nf.test and nextflow.config in the module directory to test the functionality.

- ❌ **paired_end_support:** For sequencing tools, should handle both single and paired-end data

  - **Fix:** The script only handles single-end data. Add support for paired-end data by checking meta.single_end and adding appropriate --in2 and --out2 parameters when needed.


##### Passed Requirements

- ✅ **module_naming:** Module should be named according to nf-core conventions

- ✅ **process_tag:** Process should have a tag with meta.id

- ✅ **process_label:** Process should have a resource label

- ✅ **conda_directive:** Process should have a conda directive pointing to environment.yml

- ✅ **container_directive:** Process should have a container directive with both Singularity and Docker options

- ✅ **input_output_format:** Input and output channels should be properly defined

- ✅ **versions_output:** Process should output a versions.yml file

- ✅ **when_directive:** Process should have a when directive

- ✅ **script_section:** Process should have a properly formatted script section

- ✅ **args_handling:** Process should handle task.ext.args properly

- ✅ **prefix_handling:** Process should handle task.ext.prefix properly



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/minimap2/align/main.nf`

- **Compliance Score:** 77%

- **Passed:** 10 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **ext_args:** Process should use task.ext.args for customization

  - **Fix:** Add support for task.ext.args in the script section to allow customization of minimap2 parameters. For example, add '${task.ext.args ?: ''}' to the minimap2 command.

- ❌ **module_documentation:** Module should have documentation comments

  - **Fix:** Add module documentation at the top of the file explaining the purpose, inputs, outputs, and parameters of the module.

- ❌ **samtools_version:** When using samtools in the script, its version should be included in versions.yml

  - **Fix:** Add samtools version to the versions.yml output since samtools is used for sorting and converting to BAM format.


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **process_label:** Process should have appropriate resource label

- ✅ **conda_directive:** Conda environment should be defined in environment.yml file with pinned versions

- ✅ **container_directive:** Container directive should use both Singularity and Docker options

- ✅ **input_output_format:** Input and output channels should be properly defined with meta map

- ✅ **versions_output:** Process should output software versions

- ✅ **when_directive:** Process should have a when directive for conditional execution

- ✅ **prefix_handling:** Process should use task.ext.prefix for output file naming

- ✅ **error_strategy:** Process should have appropriate error handling

- ✅ **script_formatting:** Script section should be properly formatted and readable



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/freyja/demix/main.nf`

- **Compliance Score:** 80%

- **Passed:** 12 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **meta_yml:** Module should have a meta.yml file describing inputs and outputs

  - **Fix:** Create a meta.yml file in the same directory as main.nf that describes the module, its inputs, outputs, and authors. Include detailed descriptions of input/output channel structures.

- ❌ **environment_yml:** Module should have an environment.yml file with pinned software versions

  - **Fix:** Create an environment.yml file in the same directory as main.nf with the freyja package pinned to version 1.5.2 from the bioconda channel.

- ❌ **test_config:** Module should have test configurations

  - **Fix:** Create test configurations in tests/modules/local/freyja/demix/ directory with test.yml, main.nf.test, main.nf.test.stub, and nextflow.config files to enable proper testing.


##### Passed Requirements

- ✅ **module_naming:** Module name should follow the tool/subtool format

- ✅ **process_naming:** Process name should be in uppercase with underscores

- ✅ **tag_usage:** Process should use tag with meta.id

- ✅ **label_usage:** Process should have appropriate resource label

- ✅ **conda_directive:** Conda directive should point to environment.yml file

- ✅ **container_directive:** Container directive should support both Docker and Singularity

- ✅ **input_format:** Input channels should be properly formatted

- ✅ **output_format:** Output channels should be properly formatted and include versions.yml

- ✅ **when_clause:** Process should include a when clause

- ✅ **script_section:** Script section should handle args and prefix properly

- ✅ **versions_yml:** Versions.yml should be generated correctly

- ✅ **stub_section:** Stub section should be included for testing



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/samtools/ampliconclip/main.nf`

- **Compliance Score:** 83%

- **Passed:** 15 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **environment_yml:** Module should have an environment.yml file in the same directory

  - **Fix:** Create an environment.yml file in the same directory as main.nf with pinned dependencies: name: samtools_ampliconclip
channels:
  - conda-forge
  - bioconda
  - defaults
dependencies:
  - bioconda::samtools=1.21

- ❌ **test_files:** Module should have test files (main.nf.test and nextflow.config)

  - **Fix:** Create test files for the module: main.nf.test with appropriate test cases and nextflow.config for ext.args configuration

- ❌ **documentation:** Module should have a README.md file with usage instructions

  - **Fix:** Create a README.md file documenting the module's purpose, inputs, outputs, and parameters


##### Passed Requirements

- ✅ **module_naming:** Module name should follow the nf-core naming convention

- ✅ **module_structure:** Module should have a single process with the same name as the module

- ✅ **conda_directive:** Module should have a conda directive pointing to an environment.yml file

- ✅ **container_directive:** Module should have a container directive with both Singularity and Docker options

- ✅ **process_label:** Module should have a process label

- ✅ **input_output_format:** Input and output channels should follow nf-core conventions

- ✅ **versions_output:** Module should output a versions.yml file

- ✅ **when_directive:** Module should have a when directive

- ✅ **task_ext_args:** Module should use task.ext.args for command-line arguments

- ✅ **task_ext_prefix:** Module should use task.ext.prefix for output file prefixes

- ✅ **error_handling:** Module should have appropriate error handling

- ✅ **meta_map:** Module should use meta-map for sample metadata

- ✅ **threads_usage:** Module should use task.cpus for thread allocation

- ✅ **optional_inputs:** Optional inputs should be properly marked

- ✅ **optional_outputs:** Optional outputs should be properly marked



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/fastp/main.nf`

- **Compliance Score:** 86.67%

- **Passed:** 13 requirements

- **Failed:** 2 requirements


##### Failed Requirements

- ❌ **environment_yml:** Module should have an accompanying environment.yml file

  - **Fix:** The environment.yml file is referenced in the conda directive but not provided in the component. Create an environment.yml file in the same directory with the appropriate dependencies for fastp.

- ❌ **module_test:** Module should have test configuration files

  - **Fix:** Create test configuration files for the module in the tests/modules/nf-core/fastp/ directory. Include main.nf.test and main.nf.test.snap files following nf-core guidelines.


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **process_tag:** Process should have a tag for logging

- ✅ **process_label:** Process should have a resource label

- ✅ **conda_directive:** Process should have a conda directive pointing to environment.yml

- ✅ **container_directive:** Process should have a container directive with both Singularity and Docker options

- ✅ **container_version:** Container version should be pinned

- ✅ **input_documentation:** Input channels should be properly defined

- ✅ **output_documentation:** Output channels should be properly defined with emit labels

- ✅ **versions_output:** Module should output a versions.yml file

- ✅ **when_directive:** Process should have a when directive

- ✅ **script_section:** Process should have a script section with proper variable definitions

- ✅ **stub_section:** Process should have a stub section for testing

- ✅ **code_style:** Code should follow nf-core style guidelines



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/samtools/faidx/main.nf`

- **Compliance Score:** 92.3%

- **Passed:** 12 requirements

- **Failed:** 1 requirements


##### Failed Requirements

- ❌ **multiple_inputs:** Multiple inputs should be handled correctly

  - **Fix:** The second input 'tuple val(meta2), path(fai)' uses a different meta map (meta2) than the first input. For consistency, both inputs should use the same meta map unless there's a specific reason to use different ones. Consider changing to 'tuple val(meta), path(fai)' if both inputs should share the same metadata.


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **process_label:** Process should have appropriate resource label

- ✅ **conda_directive:** Process should have conda directive pointing to environment.yml

- ✅ **container_directive:** Process should have container directive with both Singularity and Docker options

- ✅ **input_format:** Input should use tuple val(meta), path format

- ✅ **output_format:** Output should use tuple val(meta), path format and include versions.yml

- ✅ **when_directive:** Process should have a when directive

- ✅ **script_section:** Script section should use task.ext.args for arguments

- ✅ **versions_output:** Process should output software versions to versions.yml

- ✅ **stub_section:** Process should have a stub section for testing

- ✅ **optional_outputs:** Optional outputs should be marked correctly

- ✅ **output_documentation:** Output channels should be clearly named and documented



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/samtools/idxstats/main.nf`

- **Compliance Score:** 93.75%

- **Passed:** 15 requirements

- **Failed:** 1 requirements


##### Failed Requirements

- ❌ **thread_safety:** Process should handle the case when task.cpus is 1

  - **Fix:** The '--threads ${task.cpus-1}' could cause an error if task.cpus is 1. Change to '--threads ${Math.max(1, task.cpus-1)}' to ensure it's always at least 1.


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **process_tag:** Process should be tagged with meta.id

- ✅ **process_label:** Process should have appropriate resource label

- ✅ **conda_directive:** Process should have conda directive pointing to environment.yml

- ✅ **container_directive:** Process should have container directive with both Singularity and Docker options

- ✅ **container_version:** Container should be pinned to specific version

- ✅ **input_format:** Input should include meta map and required files

- ✅ **output_format:** Output should emit each file type in separate channel with meta map

- ✅ **versions_output:** Process should output versions.yml file

- ✅ **conditional_execution:** Process should have conditional execution with task.ext.when

- ✅ **script_args:** Script should use task.ext.args for additional arguments

- ✅ **prefix_handling:** Process should use task.ext.prefix or meta.id for output file naming

- ✅ **cpu_threads:** Process should properly handle CPU threads

- ✅ **stub_section:** Process should include a stub section for testing

- ✅ **versions_extraction:** Versions should be extracted correctly from tool output



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/ivar/trim/main.nf`

- **Compliance Score:** 94%

- **Passed:** 16 requirements

- **Failed:** 1 requirements


##### Failed Requirements

- ❌ **bedfile_handling:** Module handles bedfile in a non-standard way by downloading from URL or using local file

  - **Fix:** The module should not download files from URLs or copy local files within the process. Input files should be provided as proper inputs to the process. Add a new input parameter for the bedfile: 'tuple val(meta), path(bam), path(bedfile)' and remove the download/copy logic.


##### Passed Requirements

- ✅ **module_structure:** Module has correct structure with process definition, inputs, outputs, and versions

- ✅ **process_naming:** Process name follows TOOL_SUBTOOL convention in uppercase

- ✅ **process_tagging:** Process has appropriate tag with meta.id

- ✅ **process_label:** Process has appropriate resource label

- ✅ **conda_directive:** Process has conda directive pointing to environment.yml

- ✅ **container_directive:** Process has container directive with both Singularity and Docker options

- ✅ **input_format:** Input section follows correct format with meta map

- ✅ **output_format:** Output section follows correct format with named emissions

- ✅ **versions_output:** Process outputs versions.yml file

- ✅ **conditional_execution:** Process has when directive for conditional execution

- ✅ **script_section:** Script section properly formats commands and handles arguments

- ✅ **prefix_handling:** Process handles prefix correctly using task.ext.prefix or meta.id

- ✅ **args_handling:** Process handles task.ext.args correctly

- ✅ **versions_extraction:** Process correctly extracts and formats tool version information

- ✅ **meta_usage:** Module correctly uses meta map for sample identification

- ✅ **error_handling:** Module includes error handling for invalid inputs



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/multiqc/main.nf`

- **Compliance Score:** 100%

- **Passed:** 12 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_naming:** Module name should match the tool name and version

- ✅ **process_label:** Process should have an appropriate resource label

- ✅ **conda_directive:** Conda environment should be defined in an environment.yml file

- ✅ **container_directive:** Container directive should use BioContainers with proper format

- ✅ **input_definition:** Input section should be properly defined with appropriate staging

- ✅ **output_definition:** Output section should be properly defined with appropriate emit channels

- ✅ **versions_output:** Module should output a versions.yml file

- ✅ **conditional_execution:** Module should include a when directive for conditional execution

- ✅ **script_section:** Script section should properly execute the tool with appropriate arguments

- ✅ **stub_section:** Module should include a stub section for testing

- ✅ **ext_args:** Module should use task.ext.args for additional arguments

- ✅ **software_version:** Software version should be correctly captured in versions.yml



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/qualimap/bamqc/main.nf`

- **Compliance Score:** 100%

- **Passed:** 15 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_naming:** Module name should follow the nf-core naming convention

- ✅ **process_naming:** Process name should be uppercase and match the module name

- ✅ **conda_directive:** Module should have a conda directive pointing to an environment.yml file

- ✅ **container_directive:** Module should have container directives for Docker and Singularity

- ✅ **input_format:** Input section should use proper format with tuple/path declarations

- ✅ **output_format:** Output section should use proper format with tuple/path declarations and emit channels

- ✅ **versions_output:** Module should output a versions.yml file

- ✅ **when_directive:** Module should have a when directive

- ✅ **script_section:** Script section should properly handle task.ext.args and other parameters

- ✅ **stub_section:** Module should have a stub section for testing

- ✅ **meta_map:** Module should use meta map for sample metadata

- ✅ **prefix_handling:** Module should handle prefix correctly

- ✅ **resource_labels:** Module should have appropriate process resource labels

- ✅ **code_formatting:** Code should be properly formatted with consistent indentation

- ✅ **memory_handling:** Memory should be handled correctly for Java applications



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/nanoplot/main.nf`

- **Compliance Score:** 100%

- **Passed:** 13 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_name:** Module name should match the tool name and follow nf-core naming conventions

- ✅ **process_label:** Process should have appropriate resource label

- ✅ **conda_directive:** Process should have conda directive pointing to environment.yml file

- ✅ **container_directive:** Process should have container directive with appropriate BioContainers

- ✅ **input_format:** Input should use tuple val(meta), path() format

- ✅ **output_format:** Output should use tuple val(meta), path() format and include versions.yml

- ✅ **when_directive:** Process should have when directive

- ✅ **script_section:** Script section should use task.ext.args for parameters

- ✅ **versions_output:** Process should output versions.yml with correct format

- ✅ **stub_section:** Process should have a stub section for testing

- ✅ **container_version:** Container version should be pinned to specific version

- ✅ **code_style:** Code should follow nf-core style guidelines

- ✅ **environment_yml:** Module should have an environment.yml file in the same directory



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/fastqc/main.nf`

- **Compliance Score:** 100%

- **Passed:** 15 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_naming:** Module name should match the tool name

- ✅ **process_tag:** Process should have a tag with meta.id

- ✅ **process_label:** Process should have a label for computational requirements

- ✅ **conda_directive:** Process should have a conda directive pointing to environment.yml

- ✅ **container_directive:** Process should have a container directive with both Singularity and Docker options

- ✅ **input_format:** Input should use tuple val(meta), path()

- ✅ **output_format:** Output should include versions.yml and use tuple val(meta), path()

- ✅ **when_directive:** Process should have a when directive

- ✅ **ext_args:** Process should use task.ext.args for optional arguments

- ✅ **ext_prefix:** Process should use task.ext.prefix for output file naming

- ✅ **versions_output:** Process should output software version information

- ✅ **stub_block:** Process should have a stub block for testing

- ✅ **memory_handling:** Process should handle memory allocation appropriately

- ✅ **container_version:** Container version should be pinned to specific version

- ✅ **environment_yml:** Module should have an environment.yml file in the same directory



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/samtools/sort/main.nf`

- **Compliance Score:** 100%

- **Passed:** 14 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_name:** Module name should follow the format TOOL_SUBTOOL

- ✅ **process_label:** Process should have an appropriate resource label

- ✅ **conda_directive:** Module should have a conda directive pointing to an environment.yml file

- ✅ **container_directive:** Module should have a container directive with both Singularity and Docker options

- ✅ **input_format:** Input should use tuple val(meta), path() format

- ✅ **output_format:** Output should use tuple val(meta), path() format and include versions.yml

- ✅ **when_directive:** Process should have a when directive

- ✅ **ext_args:** Process should use task.ext.args for command-line arguments

- ✅ **prefix_handling:** Process should handle prefix correctly

- ✅ **versions_output:** Process should output software versions correctly

- ✅ **stub_section:** Process should have a stub section for testing

- ✅ **input_output_check:** Process should check if input and output names are the same

- ✅ **cpu_usage:** Process should use task.cpus for multi-threading

- ✅ **container_version:** Container version should be pinned to a specific version



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/samtools/index/main.nf`

- **Compliance Score:** 100%

- **Passed:** 15 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **module_tag:** Process should have a tag directive with meta.id

- ✅ **module_label:** Process should have a label directive

- ✅ **module_conda:** Process should have a conda directive pointing to environment.yml

- ✅ **module_container:** Process should have a container directive with both Singularity and Docker options

- ✅ **module_input:** Input should include meta map and input file(s)

- ✅ **module_output:** Output should emit each file type in its own channel with meta map

- ✅ **module_versions:** Module should emit a versions.yml file

- ✅ **module_when:** Module should have a when directive

- ✅ **module_script:** Script section should use task.ext.args for additional arguments

- ✅ **module_cpus:** Module should handle CPU allocation properly

- ✅ **module_stub:** Module should have a stub section for testing

- ✅ **module_output_format:** Related output file formats should be in the same channel

- ✅ **module_container_version:** Container version should be pinned to specific version

- ✅ **module_error_strategy:** Module should not define error strategy (should be in workflow)



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/samtools/flagstat/main.nf`

- **Compliance Score:** 100%

- **Passed:** 15 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **process_tag:** Process should have a tag directive with meta.id

- ✅ **process_label:** Process should have a label directive

- ✅ **conda_directive:** Process should have a conda directive pointing to environment.yml

- ✅ **container_directive:** Process should have a container directive with both Singularity and Docker options

- ✅ **container_version:** Container version should be pinned

- ✅ **input_format:** Input section should use tuple val(meta), path() format

- ✅ **output_format:** Output section should use tuple val(meta), path() format and include versions.yml

- ✅ **when_directive:** Process should have a when directive

- ✅ **script_section:** Script section should handle args, prefix, and include proper command execution

- ✅ **versions_output:** Process should output software versions to versions.yml using HEREDOC

- ✅ **stub_section:** Process should include a stub section for testing

- ✅ **threading:** Process should use task.cpus for threading when applicable

- ✅ **args_handling:** Process should handle task.ext.args properly

- ✅ **prefix_handling:** Process should handle task.ext.prefix properly



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/nf-core/samtools/stats/main.nf`

- **Compliance Score:** 100%

- **Passed:** 19 requirements

- **Failed:** 0 requirements


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **process_naming:** Process name should be uppercase and match the module name

- ✅ **tag_meta_id:** Process should be tagged with meta.id

- ✅ **process_label:** Process should have appropriate resource label

- ✅ **conda_directive:** Process should have conda directive pointing to environment.yml

- ✅ **container_directive:** Process should have container directive with both Singularity and Docker options

- ✅ **container_versioning:** Container should be version-pinned

- ✅ **input_format:** Input section should use tuple val(meta) format for sample metadata

- ✅ **output_format:** Output section should use tuple val(meta) format for sample metadata

- ✅ **versions_output:** Process should output versions.yml file

- ✅ **conditional_execution:** Process should have conditional execution with task.ext.when

- ✅ **script_section:** Script section should properly implement the tool functionality

- ✅ **args_handling:** Process should handle task.ext.args properly

- ✅ **prefix_handling:** Process should handle task.ext.prefix properly

- ✅ **cpu_threads:** Process should use task.cpus for thread count

- ✅ **stub_section:** Process should have a stub section for testing

- ✅ **versions_command:** Versions command should correctly extract tool version

- ✅ **input_index_handling:** Input index file should be properly handled

- ✅ **reference_handling:** Reference genome should be properly handled



### Nextflow_Config Components

#### nextflow.config

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/nextflow.config`

- **Compliance Score:** 77%

- **Passed:** 10 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **nf_core_branding:** Pipeline should use nf-core branding in manifest

  - **Fix:** Update manifest name to 'nf-core/aquascope' instead of 'CDCGov-Aquascope' to follow nf-core naming convention

- ❌ **syntax_error:** Config file should have valid Nextflow syntax

  - **Fix:** Remove the trailing '# Limit code size to avoid token limits' comment at the end of the plugins section which causes a syntax error

- ❌ **doi_field:** DOI field should be properly filled

  - **Fix:** Replace the placeholder space in the DOI field with an actual DOI or remove it if not available yet

- ❌ **custom_profiles:** Custom profiles should be properly documented

  - **Fix:** Add comments to explain the purpose of custom profiles like 'scicomp_rosalind', 'test_illumina', etc.


##### Passed Requirements

- ✅ **config_header:** Config file should have a proper header with pipeline name and description

- ✅ **params_structure:** Parameters should be organized in logical groups with comments

- ✅ **manifest_section:** Config should include a manifest section with required fields

- ✅ **nextflow_version:** Nextflow version should be specified with correct syntax

- ✅ **container_profiles:** Config should include standard container profiles (docker, singularity, etc.)

- ✅ **pipeline_info:** Config should include timeline, report, trace and dag sections

- ✅ **schema_plugin:** Config should include the nf-schema plugin

- ✅ **config_includes:** Config should include base and modules configs

- ✅ **environment_variables:** Config should set appropriate environment variables to prevent conflicts



### Other_File Components

#### get_software_versions.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/get_software_versions.nf`

- **Compliance Score:** 0%

- **Passed:** 0 requirements

- **Failed:** 10 requirements


##### Failed Requirements

- ❌ **module_naming:** Module name should follow nf-core conventions

  - **Fix:** This is a legacy module. nf-core now recommends using the versions.yml approach in each module instead of a centralized GET_SOFTWARE_VERSIONS process.

- ❌ **versions_yml:** Module should output a versions.yml file

  - **Fix:** Replace the current versioning approach with the standard versions.yml HEREDOC format. Each module should output its own version information.

- ❌ **container_directive:** Container directive should follow nf-core format

  - **Fix:** Update container directive to use the recommended format: container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ? 'https://depot.galaxyproject.org/singularity/python:3.8.3' : 'quay.io/biocontainers/python:3.8.3' }"

- ❌ **conda_directive:** Conda directive should specify channel and version

  - **Fix:** Update conda directive to use the recommended format: conda "conda-forge::python=3.8.3"

- ❌ **process_params:** Process should use task.ext instead of params for process-specific options

  - **Fix:** Replace params.options with task.ext.args and other task.ext properties

- ❌ **publish_dir:** publishDir should use task.ext.publishDir

  - **Fix:** Replace the publishDir directive with task.ext.publishDir configuration in the pipeline config

- ❌ **input_output_format:** Input and output channels should include meta maps

  - **Fix:** Update input and output channels to include meta maps: input: tuple val(meta), path(versions); output: tuple val(meta), path("software_versions.tsv"), emit: tsv

- ❌ **script_section:** Script section should use proper variable definitions and HEREDOC for versions

  - **Fix:** Update script section to use proper variable definitions (def prefix = task.ext.prefix ?: 'software') and include a HEREDOC for versions.yml

- ❌ **module_documentation:** Module should have proper documentation comments

  - **Fix:** Add documentation comments describing the purpose of the module, inputs, outputs, and any other relevant information

- ❌ **use_of_functions:** Module should use standard nf-core functions

  - **Fix:** Replace custom saveFiles function with standard nf-core module functions



#### functions.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/functions.nf`

- **Compliance Score:** 33%

- **Passed:** 2 requirements

- **Failed:** 4 requirements


##### Failed Requirements

- ❌ **file_location:** Utility functions should be in the lib directory

  - **Fix:** Move this file to the lib directory of your pipeline, e.g., lib/NfcoreTemplate.groovy or lib/Utils.groovy

- ❌ **code_organization:** Utility functions should be organized in a class structure

  - **Fix:** Refactor the functions into a proper Groovy class, e.g., 'class Utils { static def getSoftwareName(task_process) {...} }'

- ❌ **modern_nextflow_practices:** Use modern Nextflow practices for utility functions

  - **Fix:** These functions are from older nf-core templates. Consider using the latest nf-core template which uses task.ext directly instead of these utility functions.

- ❌ **redundant_code:** Avoid redundant utility functions that are now handled by Nextflow core

  - **Fix:** Functions like initOptions and saveFiles are no longer needed in modern nf-core pipelines as they've been replaced by task.ext functionality.


##### Passed Requirements

- ✅ **function_naming:** All function names must follow camelCase convention

- ✅ **documentation:** Functions should have proper documentation



#### kraken2_db_preparation.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/kraken2_db_preparation.nf`

- **Compliance Score:** 36%

- **Passed:** 4 requirements

- **Failed:** 7 requirements


##### Failed Requirements

- ❌ **args_usage:** Module should use task.ext.args for command-line arguments

  - **Fix:** Add 'def args = task.ext.args ?: ''' to the script section and use it in the command

- ❌ **prefix_usage:** Module should use task.ext.prefix for output file naming

  - **Fix:** Add 'def prefix = task.ext.prefix ?: db.simpleName' to the script section and use it for consistent file naming

- ❌ **meta_map:** Input should include meta map for sample metadata

  - **Fix:** Change input to include meta map: 'tuple val(meta), path(db)'

- ❌ **version_command:** Version command should extract version information directly from tool

  - **Fix:** Since tar is a standard tool, use proper version extraction: 'tar: \$(tar --version 2>&1 | sed -n 1p | sed 's/tar (GNU tar) //')'

- ❌ **environment_yml:** Module should have an accompanying environment.yml file

  - **Fix:** Create an environment.yml file in the same directory with conda dependencies: 'name: kraken2_db_preparation
channels:
  - conda-forge
  - defaults
dependencies:
  - conda-forge::sed=4.7'

- ❌ **module_documentation:** Module should have documentation comments

  - **Fix:** Add documentation comments at the top of the file explaining the purpose, inputs, outputs, and any special considerations for this module


##### Passed Requirements

- ✅ **module_structure:** Module has correct basic structure with process definition, inputs, outputs, and script section

- ✅ **module_naming:** Module name follows nf-core conventions (uppercase process name)

- ✅ **container_directive:** Container directive follows nf-core format

- ✅ **conda_directive:** Conda directive follows nf-core format with pinned channel and version

- ✅ **versions_yml:** Versions.yml file is correctly generated



#### reheader_bam.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/reheader_bam.nf`

- **Compliance Score:** 45%

- **Passed:** 5 requirements

- **Failed:** 6 requirements


##### Failed Requirements

- ❌ **module_input_output_documentation:** Input and output channels should have comments describing their structure

  - **Fix:** Add comments describing the channel structure for each input and output, e.g., '// channel: [ val(meta), path(bam) ]'

- ❌ **module_script_file:** External script files should be included in the module directory

  - **Fix:** The module uses 'reheaderbam.sh' but this script is not included in the module. Create a 'bin/reheaderbam.sh' file in the module directory.

- ❌ **module_meta_yml:** Module should have a meta.yml file with proper documentation

  - **Fix:** Create a meta.yml file in the module directory with name, description, keywords, input/output descriptions, authors, and other required metadata.

- ❌ **module_test_data:** Module should have test data references using modules_testdata_base_path

  - **Fix:** Create a test directory with main.nf.test file that references test data using params.modules_testdata_base_path

- ❌ **module_test_config:** Module should have a test configuration file

  - **Fix:** Create a nextflow.config file in the test directory with appropriate test configurations

- ❌ **module_ext_args:** Module should use ext.args for customizable parameters

  - **Fix:** Add ext.args to the script section to allow for customizable parameters, e.g., 'bash reheaderbam.sh $bam $gff ${task.ext.args ?: ''}'


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **module_conda_directive:** Conda directive should pin to channel and version but not build

- ✅ **module_container_directive:** Container directive should use the correct format for Singularity and Docker

- ✅ **module_versions_output:** Module should output software versions in the correct format

- ✅ **module_tag_usage:** Module should use the tag directive correctly



#### samplesheet_check.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/samplesheet_check.nf`

- **Compliance Score:** 45%

- **Passed:** 5 requirements

- **Failed:** 6 requirements


##### Failed Requirements

- ❌ **args_definition:** Process should use task.ext.args for command-line arguments

  - **Fix:** Add a def args = task.ext.args ?: '' line and use it in the script section with the check_samplesheet.py command

- ❌ **prefix_definition:** Process should use task.ext.prefix for output file prefixes

  - **Fix:** Add a def prefix = task.ext.prefix ?: 'samplesheet.valid' line and use it in the script section

- ❌ **meta_input:** Module should use meta map as first input channel

  - **Fix:** Add a meta map as the first input channel: input: tuple val(meta), path(samplesheet)

- ❌ **meta_output:** Module should include meta map in output channels

  - **Fix:** Include meta map in output channels: output: tuple val(meta), path('*.csv'), emit: csv

- ❌ **script_formatting:** Script section should be properly formatted with args and prefix variables

  - **Fix:** Reformat script section to use args and prefix variables

- ❌ **success_output:** The success output channel is not standard in nf-core modules

  - **Fix:** Remove the 'val true, emit: success' output and the 'echo "SUCCESS" > success.txt' command


##### Passed Requirements

- ✅ **module_naming:** Module name should follow nf-core naming conventions

- ✅ **container_directive:** Container directive should use the correct format for both Docker and Singularity

- ✅ **conda_directive:** Conda directive should specify the required software and version

- ✅ **when_statement:** Process should include a when statement that can be overridden via task.ext.when

- ✅ **versions_yml:** Process should output a versions.yml file with correct formatting



#### input_check_bam.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/modules/local/input_check_bam.nf`

- **Compliance Score:** 50%

- **Passed:** 5 requirements

- **Failed:** 5 requirements


##### Failed Requirements

- ❌ **file_location:** Local subworkflows should be placed in the subworkflows/local/ directory, not in modules/local/

  - **Fix:** Move this file to subworkflows/local/input_check_bam.nf

- ❌ **input_channels:** Input channel declarations must be defined for all possible input files within the take block

  - **Fix:** Add a take block to define input channels, e.g., 'take: input_csv'

- ❌ **documentation:** Subworkflow should have documentation comments explaining its purpose and usage

  - **Fix:** Add a comment block at the top of the file explaining the purpose of the subworkflow, its inputs, outputs, and any other relevant information

- ❌ **helper_functions:** Helper functions should be properly defined and documented

  - **Fix:** Add documentation comments to the hasExtension function explaining its purpose and parameters

- ❌ **direct_params_usage:** Avoid direct use of params in subworkflows, prefer passing values as inputs

  - **Fix:** Instead of using params.input directly, pass it as an input parameter to the subworkflow


##### Passed Requirements

- ✅ **naming_convention:** Subworkflow name should follow the nf-core naming convention (all uppercase with underscores)

- ✅ **output_channels:** Output channels should be named based on the major output file type

- ✅ **error_handling:** Error messages should be informative and help users troubleshoot issues

- ✅ **meta_map:** Meta map usage for sample information

- ✅ **file_existence_check:** Files should be checked for existence



### Schema_File Components

#### nextflow_schema.json

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/nextflow_schema.json`

- **Compliance Score:** 50%

- **Passed:** 7 requirements

- **Failed:** 7 requirements


##### Failed Requirements

- ❌ **schema_title:** The schema should have a title that follows the nf-core naming convention

  - **Fix:** Change title to 'nf-core/aquascope pipeline parameters' to follow nf-core naming convention

- ❌ **absolute_paths:** The schema should not contain hardcoded absolute file paths

  - **Fix:** Replace absolute paths in 'fasta', 'gff', and 'gff3' properties with relative paths or use parameters that can be configured by users

- ❌ **parameter_descriptions:** All parameters should have clear descriptions

  - **Fix:** Add descriptions for 'fasta', 'gff', 'gff3', 'freyja_db_name', and 'bed' parameters

- ❌ **parameter_organization:** Parameters should be organized in appropriate sections

  - **Fix:** Move reference-related parameters ('fasta', 'gff', 'gff3', 'bed') to a dedicated reference section in the schema

- ❌ **parameter_validation:** Parameters should have appropriate validation rules

  - **Fix:** Add validation rules (exists, format, etc.) for reference files like 'fasta', 'gff', 'gff3', and 'bed'

- ❌ **fa_icons:** Parameters should have appropriate Font Awesome icons

  - **Fix:** Add fa_icon properties for 'fasta', 'gff', 'gff3', 'freyja_db_name', and 'bed' parameters

- ❌ **help_text:** Complex parameters should have help_text for additional explanation

  - **Fix:** Add help_text for reference parameters to explain their purpose and format requirements


##### Passed Requirements

- ✅ **schema_structure:** The schema file should follow the JSON schema draft 2020-12 format

- ✅ **schema_id:** The schema should have a valid $id URL pointing to the repository

- ✅ **schema_description:** The schema should have a clear description of the pipeline purpose

- ✅ **schema_sections:** The schema should have appropriate sections for different parameter groups

- ✅ **institutional_config:** The schema should include standard institutional config options

- ✅ **generic_options:** The schema should include standard generic options

- ✅ **input_output_options:** The schema should have well-defined input/output options



### Subworkflow Components

#### input_check.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/local/input_check.nf`

- **Compliance Score:** 40%

- **Passed:** 4 requirements

- **Failed:** 6 requirements


##### Failed Requirements

- ❌ **sw_input_channel_comments:** Each input channel should have a comment describing the structure

  - **Fix:** Add comments describing the input channel structure at the beginning of the workflow, e.g., '// input: params.input // string: path to input CSV file or glob pattern for fastq files'

- ❌ **sw_output_channel_comments:** Each output channel should have a comment describing the structure

  - **Fix:** Add comments describing the output channel structure in the emit block, e.g., '// channel: [ val(meta), path(fastq) ]' for each emitted channel

- ❌ **sw_output_channel_naming:** Output channel names should be based on the major output file type

  - **Fix:** Rename output channels to match the content type without prefixes like 'raw_'. For example, 'raw_short_reads' should be 'short_reads', 'raw_long_reads' should be 'long_reads', and 'raw_bam' should be 'bam'

- ❌ **sw_meta_yml:** Subworkflow should have a meta.yml file with channel structure documentation

  - **Fix:** Create a meta.yml file in the same directory with input and output channel descriptions, author information, and other metadata

- ❌ **sw_function_location:** Helper functions should be defined in a separate file or at the top of the file

  - **Fix:** Move the 'hasExtension' function to a separate utilities file or clearly separate it from the workflow definition with additional comments

- ❌ **sw_test_file:** Subworkflow should have associated tests

  - **Fix:** Create a tests directory with main.nf.test file that tests the subworkflow functionality using nf-test


##### Passed Requirements

- ✅ **sw_naming:** Subworkflow name should be in uppercase with underscores

- ✅ **sw_required_input_channels:** Input channel declarations must be defined for all possible input files

- ✅ **sw_header_comment:** Subworkflow should have a descriptive header comment

- ✅ **sw_error_handling:** Proper error messages should be provided for invalid inputs



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/nf-core/utils_nfschema_plugin/main.nf`

- **Compliance Score:** 40%

- **Passed:** 4 requirements

- **Failed:** 6 requirements


##### Failed Requirements

- ❌ **1.1:** Minimum subworkflow size - must contain at least two modules

  - **Fix:** This subworkflow doesn't contain any modules. It only includes functions from the nf-schema plugin. Consider adding at least two modules or reclassifying this as a utility function rather than a subworkflow.

- ❌ **1.2:** Version reporting channel - must emit versions channel

  - **Fix:** Add a versions channel to collect and emit version information. Example: `ch_versions = Channel.empty()` and then `emit: versions = ch_versions`

- ❌ **2.5:** Input channel name structure - should signify input object type

  - **Fix:** Rename input parameters to follow the convention: prefix single value inputs with 'val_' (e.g., 'val_validate_params', 'val_parameters_schema') and channel inputs with 'ch_' (e.g., 'ch_input_workflow').

- ❌ **2.6:** Output channel name structure

  - **Fix:** Rename 'dummy_emit' to follow proper naming conventions. Consider using a more descriptive name like 'ch_validated' or similar that indicates the purpose of the output.

- ❌ **5.1:** Code comment of channel structure

  - **Fix:** Add detailed comments for each input and output channel describing their structure. For example: `// workflow: [mandatory] the workflow object used by nf-schema to get metadata from the workflow`

- ❌ **5.2:** Meta.yml documentation of channel structure

  - **Fix:** Create a meta.yml file in the same directory with detailed descriptions of input and output channel structures.


##### Passed Requirements

- ✅ **2.1:** Name format of subworkflow files

- ✅ **2.2:** Name format of subworkflow parameters - must follow snake_case

- ✅ **2.3:** Name format of subworkflow functions - must follow camelCase

- ✅ **2.4:** Name format of subworkflow channels - must follow snake_case



#### ont_trimming.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/local/ont_trimming.nf`

- **Compliance Score:** 42.86%

- **Passed:** 3 requirements

- **Failed:** 4 requirements


##### Failed Requirements

- ❌ **4.1:** Usage of parameters

  - **Fix:** The subworkflow directly uses params.fasta from the parent workflow. This should be passed as an input parameter to the subworkflow instead. Modify the workflow to accept fasta as an input parameter.

- ❌ **5.1:** Code comment of channel structure

  - **Fix:** Add comments describing the structure of input channels. For example: 'bam // channel: [mandatory] meta, bam', 'val_saverejects // boolean: [mandatory]', etc.

- ❌ **5.2:** Meta.yml documentation of channel structure

  - **Fix:** Create a meta.yml file for the subworkflow that describes the input and output channel structures.

- ❌ **6.8:** Configuration for nf-tests

  - **Fix:** Create a nextflow.config file for testing the subworkflow that supplies ext.args to the modules.


##### Passed Requirements

- ✅ **1.1:** Minimum subworkflow size

- ✅ **1.2:** Version reporting channel

- ✅ **2.1:** Name format of subworkflow files



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/local/freyja_variant_demix_update/main.nf`

- **Compliance Score:** 62.5%

- **Passed:** 5 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **5.2:** Meta.yml documentation of channel structure

  - **Fix:** Create a meta.yml file in the same directory as main.nf that documents the input and output channel structures.

- ❌ **6.1:** Scope of testing

  - **Fix:** Create tests for the subworkflow using nf-test. At minimum, implement a stub test that replicates the generation of output files.

- ❌ **6.8:** Configuration for tests

  - **Fix:** Create a nextflow.config file for tests that supplies ext.args to the modules used in the subworkflow.


##### Passed Requirements

- ✅ **1.1:** Minimum subworkflow size

- ✅ **1.2:** Version reporting channel

- ✅ **2.1:** Name format of subworkflow files

- ✅ **4.1:** Usage of parameters

- ✅ **5.1:** Code comment of channel structure



#### trimming.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/local/trimming.nf`

- **Compliance Score:** 67%

- **Passed:** 8 requirements

- **Failed:** 4 requirements


##### Failed Requirements

- ❌ **2.5:** Input channel name structure

  - **Fix:** The input channel 'bam' should be prefixed with 'ch_' to indicate it's a channel with multiple elements.

- ❌ **4.1:** Usage of parameters

  - **Fix:** The subworkflow directly uses 'params.fasta' which should be avoided. Instead, the fasta file should be passed as an input parameter to the subworkflow.

- ❌ **5.1:** Code comment of channel structure

  - **Fix:** The input channel 'bam' is missing a comment describing its structure. Add a comment like: // channel: [ val(meta), path(bam) ]

- ❌ **5.2:** Meta.yml documentation of channel structure

  - **Fix:** A meta.yml file is required for the subworkflow to document the input and output channel structures.

- ❌ **6.8:** Configuration for nf-tests

  - **Fix:** No evidence of nf-test configuration. A nextflow.config file should be created for testing this subworkflow.


##### Passed Requirements

- ✅ **1.1:** Minimum subworkflow size

- ✅ **1.2:** Version reporting channel

- ✅ **2.1:** Name format of subworkflow files

- ✅ **2.2:** Name format of subworkflow parameters

- ✅ **2.3:** Name format subworkflow functions

- ✅ **2.4:** Name format subworkflow channels

- ✅ **2.6:** Output channel name structure



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/nf-core/utils_nextflow_pipeline/main.nf`

- **Compliance Score:** 67%

- **Passed:** 6 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **subworkflow_size:** Subworkflow must contain at least two modules

  - **Fix:** This subworkflow doesn't contain any modules. It should include at least two modules or be refactored as a utility function if it's meant to be a collection of helper functions.

- ❌ **version_reporting:** Each subworkflow should emit a channel containing all versions.yml collecting the tool(s) versions

  - **Fix:** Add a versions channel to collect and emit tool versions. For example: 'ch_versions = Channel.empty()' in the take: section and 'versions = ch_versions' in the emit: section.

- ❌ **meaningful_emit:** Subworkflow should emit meaningful outputs

  - **Fix:** Replace 'dummy_emit = true' with meaningful outputs that represent the actual results of the subworkflow's operations.


##### Passed Requirements

- ✅ **subworkflow_naming:** Subworkflow name should follow the nf-core naming convention

- ✅ **input_output_documentation:** Subworkflow should have clear documentation for inputs and outputs

- ✅ **header_documentation:** Subworkflow should have a header with description

- ✅ **function_documentation:** Functions should be properly documented

- ✅ **error_handling:** Subworkflow should include appropriate error handling

- ✅ **code_organization:** Code should be well-organized with clear sections



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/nf-core/utils_nfcore_pipeline/main.nf`

- **Compliance Score:** 70%

- **Passed:** 7 requirements

- **Failed:** 3 requirements


##### Failed Requirements

- ❌ **minimum_size:** Subworkflow must contain at least two modules

  - **Fix:** This subworkflow doesn't contain any modules. It only contains utility functions. Consider either adding modules or reclassifying this as a utility script rather than a subworkflow.

- ❌ **nf_test:** Subworkflow should have associated nf-test files

  - **Fix:** Create nf-test files for this subworkflow in the tests/subworkflows/nf-core/utils_nfcore_pipeline/ directory with appropriate test cases.

- ❌ **test_config:** Subworkflow tests should use a single nextflow.config file

  - **Fix:** Create a nextflow.config file for tests that supplies ext.args to the subworkflow.


##### Passed Requirements

- ✅ **naming_convention:** Subworkflow name should follow the nf-core naming convention (lowercase with underscores)

- ✅ **directory_structure:** Subworkflow should be in the correct directory structure (subworkflows/nf-core/)

- ✅ **workflow_definition:** Subworkflow should have a clear workflow definition with input/output channels

- ✅ **documentation:** Subworkflow should have appropriate documentation and comments

- ✅ **version_reporting:** Subworkflow should include version reporting functionality

- ✅ **input_output_definition:** Subworkflow should have clearly defined input and output channels

- ✅ **function_organization:** Functions should be properly organized and documented



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/local/bam_sort_stats_samtools/main.nf`

- **Compliance Score:** 80%

- **Passed:** 8 requirements

- **Failed:** 2 requirements


##### Failed Requirements

- ❌ **5.2:** Meta.yml documentation of channel structure

  - **Fix:** Create a meta.yml file in the same directory as main.nf that describes the subworkflow purpose, inputs, outputs and authors. Include detailed descriptions of the channel structures in this file.

- ❌ **9.1:** Proper documentation

  - **Fix:** Add a README.md file to the subworkflow directory explaining its purpose, usage, and examples.


##### Passed Requirements

- ✅ **1.1:** Minimum subworkflow size

- ✅ **1.2:** Version reporting channel

- ✅ **2.1:** Name format of subworkflow files

- ✅ **4.1:** Usage of parameters

- ✅ **5.1:** Code comment of channel structure

- ✅ **6.1:** Consistent module imports

- ✅ **7.1:** Proper channel handling

- ✅ **8.1:** Proper error handling



#### main.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/subworkflows/local/utils_nfcore_aquascope_pipeline/main.nf`

- **Compliance Score:** 82%

- **Passed:** 9 requirements

- **Failed:** 2 requirements


##### Failed Requirements

- ❌ **sw_commented_code:** Subworkflow should not contain commented-out code blocks that are not used

  - **Fix:** Remove or implement the commented-out code block for creating channel from input file. If this is intended for future use, add a TODO comment explaining why it's commented out.

- ❌ **sw_todo_comments:** TODO comments should be properly formatted and actionable

  - **Fix:** The TODO comments in the toolCitationText and toolBibliographyText functions should include specific instructions or be removed if they are no longer needed.


##### Passed Requirements

- ✅ **sw_general_size:** A subworkflow must contain at least two modules

- ✅ **sw_version_reporting:** Subworkflow should have a version reporting channel

- ✅ **sw_naming_convention:** Subworkflow name should follow the naming convention (all caps with underscores)

- ✅ **sw_documentation:** Subworkflow should have appropriate documentation comments

- ✅ **sw_input_output:** Subworkflow should have clearly defined input and output channels

- ✅ **sw_organization:** Subworkflow should be well-organized with clear sections

- ✅ **sw_imports:** Subworkflow should properly import all required modules and functions

- ✅ **sw_error_handling:** Subworkflow should include appropriate error handling

- ✅ **sw_function_documentation:** Functions within the subworkflow should be properly documented



### Workflow Components

#### quality_align.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/workflows/quality_align.nf`

- **Compliance Score:** 36%

- **Passed:** 4 requirements

- **Failed:** 7 requirements


##### Failed Requirements

- ❌ **workflow_structure:** Workflow should have proper structure with input/output definitions

  - **Fix:** Add proper input and output definitions to the workflow. The workflow should have explicit input and output blocks. Example: 'workflow runQualityAlign { input: ... output: ... }'

- ❌ **channel_documentation:** Each input and output channel should have a comment describing its structure

  - **Fix:** Add comments to describe the structure of each input and output channel. For example: '// channel: [ val(meta), path(reads) ]'

- ❌ **emit_versions:** Workflow should emit a versions channel

  - **Fix:** Add an explicit emit block that includes the versions channel. Example: 'emit: versions = ch_versions // channel: [ path(versions.yml) ]'

- ❌ **parameter_usage:** Named params from parent workflow should not be assumed to be passed to the workflow

  - **Fix:** Instead of directly using params.* variables, pass them as input parameters to the workflow or use input value channels

- ❌ **workflow_documentation:** Workflow should have comprehensive documentation

  - **Fix:** Add a meta.yml file for the workflow that describes its purpose, inputs, outputs, and usage examples

- ❌ **test_configuration:** Workflow should have proper test configuration

  - **Fix:** Create test files for the workflow including main.nf.test and nextflow.config for testing

- ❌ **error_handling:** Workflow should include proper error handling

  - **Fix:** Add error handling for critical operations, especially for file existence checks and channel operations


##### Passed Requirements

- ✅ **workflow_naming:** Workflow name should follow camelCase convention

- ✅ **code_organization:** Code should be well-organized with logical sections

- ✅ **dsl2_compliance:** Workflow should use DSL2 syntax

- ✅ **module_inclusion:** Modules and subworkflows should be properly included



#### freyja_only.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/workflows/freyja_only.nf`

- **Compliance Score:** 50%

- **Passed:** 6 requirements

- **Failed:** 6 requirements


##### Failed Requirements

- ❌ **channel_documentation:** Input and output channels should have comments describing their structure

  - **Fix:** Add comments to input and output channels describing their structure, e.g., 'ch_sorted_bam // channel: [mandatory] meta, bam' and 'multiqc_report // channel: [ path(multiqc_report.html) ]'

- ❌ **meta_yml:** Workflow should have a meta.yml file with documentation

  - **Fix:** Create a meta.yml file in the same directory as the workflow with name, description, keywords, and documentation of input/output channels

- ❌ **parameter_usage:** Named params from parent workflow should not be assumed to be passed to the workflow

  - **Fix:** Refactor to pass all required parameters as input channels rather than directly accessing params.* variables within the workflow

- ❌ **test_data_reference:** Test data should be referenced with modules_testdata_base_path parameter

  - **Fix:** When creating tests for this workflow, ensure test data is referenced using params.modules_testdata_base_path

- ❌ **workflow_documentation:** Workflow should have header documentation explaining its purpose

  - **Fix:** Add a header comment section explaining the purpose of the workflow, its inputs, outputs, and how it should be used

- ❌ **test_configuration:** Workflow tests should use a single nextflow.config for ext.args

  - **Fix:** Create a nextflow.config file for tests that supplies ext.args to the workflow processes


##### Passed Requirements

- ✅ **workflow_naming:** Workflow name should follow camelCase convention

- ✅ **workflow_structure:** Workflow should have proper take/main/emit structure

- ✅ **version_tracking:** Workflow should collect and emit software versions

- ✅ **error_handling:** Workflow should have proper error handling

- ✅ **channel_naming:** Channel names should be descriptive and consistent

- ✅ **code_formatting:** Code should be properly formatted and indented



#### aquascope.nf

- **Path:** `/Users/arunbodd/Documents/Work/Nextflow_pipelines/aquascope/workflows/aquascope.nf`

- **Compliance Score:** 50%

- **Passed:** 5 requirements

- **Failed:** 5 requirements


##### Failed Requirements

- ❌ **workflow_functionality:** Workflow should contain actual processing steps

  - **Fix:** The workflow is missing actual processing steps. It only collects versions but doesn't perform any data processing. Add modules or subworkflows that process the input samplesheet data.

- ❌ **input_validation:** Workflow should validate inputs

  - **Fix:** Add input validation for the samplesheet channel to ensure it contains the expected format and data.

- ❌ **documentation:** Workflow should have header comments explaining its purpose

  - **Fix:** Add header comments that explain the purpose of the workflow, expected inputs, and outputs.

- ❌ **error_handling:** Workflow should include error handling for critical steps

  - **Fix:** Add error handling for critical processing steps to provide meaningful error messages when failures occur.

- ❌ **output_organization:** Workflow should organize outputs in a structured manner

  - **Fix:** Define and organize workflow outputs beyond just version information. Include processed data outputs in the emit section.


##### Passed Requirements

- ✅ **workflow_name:** Workflow name should be in uppercase and match the file name

- ✅ **workflow_structure:** Workflow should have proper take/main/emit structure

- ✅ **version_reporting:** Workflow should collect and report software versions

- ✅ **minimum_inputs:** Workflow should be able to run with minimal required inputs

- ✅ **channel_naming:** Channel names should be descriptive and follow conventions



## Recommendations

Based on the validation results, here are the top recommendations to improve compliance:


1. **Fix environment_yml violations** (6 occurrences)

   - *Issue:* Module should have an accompanying environment.yml file

   - *Recommendation:* Create an environment.yml file in the same directory with conda dependencies: 'name: kraken2_db_preparation
channels:
  - conda-forge
  - defaults
dependencies:
  - conda-forge::sed=4.7'



2. **Fix 5.2 violations** (5 occurrences)

   - *Issue:* Meta.yml documentation of channel structure

   - *Recommendation:* Create a meta.yml file for the subworkflow that describes the input and output channel structures.



3. **Fix module_documentation violations** (4 occurrences)

   - *Issue:* Module should have documentation comments

   - *Recommendation:* Add documentation comments at the top of the file explaining the purpose, inputs, outputs, and any special considerations for this module



4. **Fix documentation violations** (3 occurrences)

   - *Issue:* Subworkflow should have documentation comments explaining its purpose and usage

   - *Recommendation:* Add a comment block at the top of the file explaining the purpose of the subworkflow, its inputs, outputs, and any other relevant information



5. **Fix test_files violations** (3 occurrences)

   - *Issue:* Module should have test files (main.nf.test and nextflow.config)

   - *Recommendation:* Create test files for the module: main.nf.test and nextflow.config in a tests/ directory to ensure the module can be properly tested.



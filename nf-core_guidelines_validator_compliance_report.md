# nf-core Pipeline Compliance Report

**Pipeline:** `nf-core_guidelines_validator`

**Path:** `/Users/arunbodd/Documents/Work/nf-core_guidelines_validator`

**Date:** 2025-07-04 16:39:08

**nf-core Validator Version:** 0.1.0


## Summary

- **Components Analyzed:** 1

- **Requirements Checked:** 18

- **Passed Requirements:** 0

- **Failed Requirements:** 18

- **Compliance Score:** 0.0%


## Classification Compliance Breakdown

| Classification | Definition | Category | Subcategory | Files not passing the definition |

|---------------|------------|----------|-------------|----------------------------------|



## Component Type Breakdown

| Component Type | Count | Avg. Compliance |

|---------------|-------|----------------|

| unknown | 1 | 0.00% |



## Component Details

### Unknown Components

#### nf-core_guidelines_validator

- **Path:** `/Users/arunbodd/Documents/Work/nf-core_guidelines_validator`

- **Compliance Score:** 0.0%

- **Passed:** 0 requirements

- **Failed:** 18 requirements


##### Failed Requirements

- ❌ **Category: Module Subcategory: Resource requirement:** Category: Module Subcategory: Resource requirements Definition: An appropriate resource label must be provided for the module as listed in the nf-core pipeline template e.g. process_single, process_lo

- ❌ **Category: Workflow Subcategory: Documentation Defi:** Category: Workflow Subcategory: Documentation Definition: Publication credit: Pipeline publications should acknowledge the nf-core community.

- ❌ **Category: Workflow Subcategory: General Definition:** Category: Workflow Subcategory: General Definition: Use the template: All nf-core pipelines must be built using the nf-core template and pipeline initialization with nf-core create (nf-core/tools vers

- ❌ **Category: Workflow Subcategory: Testing Definition:** Category: Workflow Subcategory: Testing Definition: Pass lint tests: The pipeline must not have any undocumented failures in the?nf-core lint?tests.

- ❌ **Category: Subworkflow Subcategory: Testing Definit:** Category: Subworkflow Subcategory: Testing Definition: All output channels should be present in the nf-test snapshot file, or at a minimum, it must be verified that the files exist.

- ❌ **Category: Test Data Subcategory: Test Data Definit:** Category: Test Data Subcategory: Test Data Definition: Test data files must have an entry in the nf-core/test-datasets repo README

- ❌ **Category: Subworkflow Subcategory: I/O options Def:** Category: Subworkflow Subcategory: I/O options Definition: Input channel declarations must be defined for all possible input files that will be required by the subworkflow (i.e. both required and opti

- ❌ **Category: Module Subcategory: Software requirement:** Category: Module Subcategory: Software requirements Definition: Software requirements should be declared within the module file using the Nextflow container directive

- ❌ **Category: Subworkflow Subcategory: General Definit:** Category: Subworkflow Subcategory: General Definition: Subworkflow must contain at least two modules

- ❌ **Category: Module Subcategory: General Definition: :** Category: Module Subcategory: General Definition: Modules should be stored in the modules dir, and local modules should follow the same dir structure and naming conventions as nf-core modules

- ❌ **Category: Subworkflow Subcategory: Documentation D:** Category: Subworkflow Subcategory: Documentation Definition: Each input and output channel structure should also be described in the meta.yml in the description entry.

- ❌ **Category: Module Subcategory: I/O options Definiti:** Category: Module Subcategory: I/O options Definition: Input channel val declarations should be defined for all mandatory non-file inputs that are essential for the functioning of the tool (e.g. parame

- ❌ **Category: Subworkflow Subcategory: Naming conventi:** Category: Subworkflow Subcategory: Naming conventions Definition: All parameter names must follow the snake_case convention

- ❌ **Category: Module Subcategory: Naming conventions D:** Category: Module Subcategory: Naming conventions Definition: Directory structure for the module name must be all lowercase, and without punctuation, e.g. modules/nf-core/bwa/mem/. The name of the soft

- ❌ **Category: Subworkflow Subcategory: Parameters Defi:** Category: Subworkflow Subcategory: Parameters Definition: Named params defined in the parent workflow must not be assumed to be passed to the subworkflow to allow developers to call their parameters w

- ❌ **Category: Module Subcategory: Documentation Defini:** Category: Module Subcategory: Documentation Definition: Input entries should be marked as Mandatory or Optional

- ❌ **Category: Module Subcategory: Testing Definition: :** Category: Module Subcategory: Testing Definition: Testing data for custom modules should be accessible (e.g., https://github.com/nf-core/test-datasets).

- ❌ **Category: Module Subcategory: Parameters Definitio:** Category: Module Subcategory: Parameters Definition: Any parameters that need to be evaluated in the context of a particular sample e.g. single-end/paired-end data must also be defined within the proc



## Recommendations

Based on the validation results, here are the top recommendations to improve compliance:


# Test Documentation

> **Auto-generated** on 2025-11-02 14:51:34 
> **Total Tests**: 329

This page provides a comprehensive overview of all tests in the project, automatically extracted from test docstrings.

## E2E Tests

| Test Class | Test Name | Description |
|------------|-----------|-------------|
| TestCLICompletion | `test_complete_namespaces` | Test --complete outputs list of available namespaces. |
| TestCLICompletion | `test_complete_partial_namespace` | Test --complete filters namespaces by partial prefix match. |
| TestCLICompletion | `test_complete_partial_task_name` | Test --complete filters task names by partial prefix match. |
| TestCLICompletion | `test_complete_task_names` | Test --complete outputs task names for namespace:task completion. |
| TestCLICompletion | `test_completion_bash` | Test --completion bash outputs bash shell completion script. |
| TestCLICompletion | `test_completion_fish` | Test --completion fish outputs fish shell completion script. |
| TestCLICompletion | `test_completion_unknown_shell` | Test --completion with unsupported shell returns error. |
| TestCLICompletion | `test_completion_zsh` | Test --completion zsh outputs zsh shell completion script. |
| TestCLICompletion | `test_install_completion_auto_detect` | Test --install-completion auto-detects shell from SHELL environment variable. |
| TestCLICompletion | `test_install_completion_bash` | Test --install-completion bash installs completion script to user directory. |
| TestCLIHelp | `test_console_script_help` | Test CLI displays help when invoked as console script. |
| TestCLIHelp | `test_main_with_none_argv` | Test main() accepts None as argv parameter. |
| TestCLIHelp | `test_python_module_help` | Test CLI displays help when invoked as Python module. |
| TestCLIInvalidCommand | `test_invalid_command_error` | Test error message for invalid command. |
| TestCLISearch | `test_namespace_command_help` | Test namespace command help displays meta-namespace documentation. |
| TestCLISearch | `test_search_combined_filters` | Test combining pattern and --regex applies AND logic to filters. |
| TestCLISearch | `test_search_command_help` | Test search command help displays filter options and examples. |
| TestCLISearch | `test_search_description_match` | Test search matches text in task descriptions. |
| TestCLISearch | `test_search_group_match` | Test search displays all tasks when pattern matches group name. |
| TestCLISearch | `test_search_invalid_regex` | Test search handles invalid regex patterns gracefully. |
| TestCLISearch | `test_search_json_output` | Test --json flag outputs search results in JSON format. |
| TestCLISearch | `test_search_json_structure` | Test search JSON output contains required result fields. |
| TestCLISearch | `test_search_missing_pattern_error` | Test search command requires at least one search filter. |
| TestCLISearch | `test_search_multiple_namespaces` | Test search returns matching tasks across all namespaces. |
| TestCLISearch | `test_search_namespace_match` | Test search displays all tasks when pattern matches namespace name. |
| TestCLISearch | `test_search_no_results` | Test search displays appropriate message when no tasks match. |
| TestCLISearch | `test_search_pattern_basic` | Test pattern search matches task names containing the pattern. |
| TestCLISearch | `test_search_pattern_case_insensitive` | Test pattern search performs case-insensitive matching. |
| TestCLISearch | `test_search_regex_basic` | Test --regex flag enables regular expression pattern matching. |
| TestCLISearch | `test_search_regex_end_anchor` | Test regex search supports word boundary anchors. |
| TestCLISearch | `test_search_with_no_color` | Test --no-color flag disables ANSI color codes in search output. |
| TestCLISearch | `test_search_with_search_dirs` | Test search command respects --search-dirs option. |
| TestCLISearch | `test_search_with_verbose` | Test --verbose flag displays search directory information. |
| TestCLIValidation | `test_invalid_task_structure_shows_warning` | Test invalid task structure displays warnings but continues processing. |
| TestCLIValidation | `test_invalid_version_shows_warning` | Test invalid Taskfile version displays warning but continues processing. |
| TestCLIValidation | `test_invalid_yaml_syntax_shows_warning` | Test invalid YAML syntax displays warning but continues processing. |
| TestCLIValidation | `test_missing_version_shows_warning` | Test missing Taskfile version displays warning but continues processing. |
| TestCLIValidation | `test_valid_taskfile_no_warnings` | Test valid Taskfile produces no validation warnings. |
| TestCLIWithTaskfiles | `test_all_namespace_shows_all_namespaces` | Test 'all' meta-namespace displays tasks from all namespaces. |
| TestCLIWithTaskfiles | `test_all_namespace_with_color` | Test 'all' meta-namespace works with color output enabled. |
| TestCLIWithTaskfiles | `test_json_output` | Test --json flag outputs tasks in JSON format. |
| TestCLIWithTaskfiles | `test_json_output_no_color_codes` | Test JSON output never contains ANSI color codes. |
| TestCLIWithTaskfiles | `test_no_color_from_current_dir` | Test --no-color flag disables ANSI color codes in output. |
| TestCLIWithTaskfiles | `test_no_taskfile_error` | Test CLI returns error when no Taskfile is found. |
| TestCLIWithTaskfiles | `test_nonexistent_namespace` | Test requesting nonexistent namespace returns error with suggestions. |
| TestCLIWithTaskfiles | `test_piped_output_no_color` | Test piped output automatically disables ANSI color codes. |
| TestCLIWithTaskfiles | `test_question_mark_lists_namespaces` | Test '?' meta-namespace displays list of available namespaces. |
| TestCLIWithTaskfiles | `test_search_dirs_option` | Test --search-dirs option locates Taskfiles in specified directory. |
| TestCLIWithTaskfiles | `test_search_dirs_with_multiple_paths` | Test --search-dirs accepts multiple colon-separated directory paths. |
| TestCLIWithTaskfiles | `test_specific_namespace` | Test namespace command displays tasks from specified namespace. |
| TestCLIWithTaskfiles | `test_verbose_output` | Test --verbose flag displays search directory information. |

## Unit Tests

| Test Class | Test Name | Description |
|------------|-----------|-------------|
| TestArgs | `test_parse_args_all_namespace` | Test parsing args with 'all' namespace. |
| TestArgs | `test_parse_args_default` | Test parsing args with defaults. |
| TestArgs | `test_parse_args_json` | Test parsing args with --json flag. |
| TestArgs | `test_parse_args_namespace` | Test parsing args with namespace. |
| TestArgs | `test_parse_args_namespace_with_no_color` | Test parsing namespace with --no-color flag. |
| TestArgs | `test_parse_args_namespace_with_search_dirs` | Test parsing namespace with --search-dirs. |
| TestArgs | `test_parse_args_namespace_with_verbose` | Test parsing namespace with --verbose flag. |
| TestArgs | `test_parse_args_no_color` | Test parsing args with --no-color flag. |
| TestArgs | `test_parse_args_search_dirs` | Test parsing args with --search-dirs. |
| TestArgs | `test_parse_args_search_dirs_short` | Test parsing args with -s short option. |
| TestArgs | `test_parse_args_verbose` | Test parsing args with --verbose flag. |
| TestArgs | `test_parse_args_verbose_short` | Test parsing args with -v short option. |
| TestColors | `test_colors_enabled_by_default` | Test colors are enabled by default. |
| TestColors | `test_disable_colors` | Test disabling colors. |
| TestCompleteFlags | `test_completes_long_flags` | Test completing long flags. |
| TestCompleteFlags | `test_completes_short_flags` | Test completing short flags. |
| TestCompleteFlags | `test_returns_all_flags_for_dash` | Test that all flags starting with - are returned. |
| TestCompleteFlags | `test_returns_empty_for_non_flag` | Test that empty list is returned for non-flag input. |
| TestCompleteNamespace | `test_discovers_namespace_taskfiles` | Test that namespace taskfiles are discovered. |
| TestCompleteNamespace | `test_filters_by_partial_match` | Test filtering namespaces by partial match. |
| TestCompleteNamespace | `test_returns_main_and_all` | Test that main and all are always included. |
| TestCompleteTaskName | `test_completes_tasks_in_main_namespace` | Test completing task names in main namespace. |
| TestCompleteTaskName | `test_completes_tasks_in_namespace` | Test completing task names within a namespace. |
| TestCompleteTaskName | `test_handles_parse_taskfile_exception` | Test that exceptions from parse_taskfile are caught and handled. |
| TestCompleteTaskName | `test_handles_parsing_errors_gracefully` | Test that parsing errors are handled gracefully. |
| TestCompleteTaskName | `test_returns_empty_for_nonexistent_namespace` | Test that empty list is returned for nonexistent namespace. |
| TestConfig | `test_config_all_namespace` | Test 'all' namespace. |
| TestConfig | `test_config_args_override_pyproject` | Test command line args override pyproject.toml. |
| TestConfig | `test_config_colorize_no_color_flag` | Test colorize disabled with --no-color flag. |
| TestConfig | `test_config_colorize_no_tty` | Test colorize disabled when output is not TTY. |
| TestConfig | `test_config_colorize_tty` | Test colorize enabled when output is TTY. |
| TestConfig | `test_config_default_search_dir` | Test config with default search directory. |
| TestConfig | `test_config_empty_search_dirs_defaults_to_cwd` | Test empty search dirs defaults to current directory. |
| TestConfig | `test_config_group_pattern_from_taskfile_help_yml` | Test group-pattern setting from taskfile_help.yml. |
| TestConfig | `test_config_namespace_property` | Test namespace property. |
| TestConfig | `test_config_no_color_from_taskfile_help_yml` | Test no-color setting from taskfile_help.yml. |
| TestConfig | `test_config_removes_duplicate_search_dirs` | Test duplicate search directories are removed. |
| TestConfig | `test_config_removes_duplicate_search_dirs_order` | Test duplicate search directories preserve first occurrence order. |
| TestConfig | `test_config_resolves_relative_paths` | Test relative paths are resolved to absolute paths. |
| TestConfig | `test_config_search_dirs_from_args` | Test config with search dirs from command line. |
| TestConfig | `test_config_search_dirs_from_pyproject` | Test config with search dirs from pyproject.toml as list. |
| TestConfig | `test_config_search_dirs_from_pyproject_empty_string` | Test config with search dirs from pyproject.toml as empty string. |
| TestConfig | `test_config_search_dirs_from_pyproject_list_with_empty` | Test config with search dirs from pyproject.toml list containing empty strings. |
| TestConfig | `test_config_search_dirs_from_pyproject_single_string` | Test config with search dirs from pyproject.toml as single string. |
| TestConfig | `test_config_search_dirs_from_taskfile_help_yml` | Test config with search dirs from taskfile_help.yml. |
| TestConfig | `test_config_taskfile_help_yml_takes_precedence` | Test taskfile_help.yml takes precedence over pyproject.toml. |
| TestConfigEdgeCases | `test_config_nonexistent_search_dir` | Test config with non-existent search directory. |
| TestConfigEdgeCases | `test_config_search_dirs_with_spaces` | Test search dirs with spaces in path names. |
| TestConfigEdgeCases | `test_load_config_permission_error` | Test loading config when pyproject.toml is not readable. |
| TestEnvironmentVariableEdgeCases | `test_no_color_case_insensitive` | TASKFILE_HELP_NO_COLOR is case-insensitive. |
| TestEnvironmentVariableEdgeCases | `test_no_color_yes_uppercase` | TASKFILE_HELP_NO_COLOR=YES (uppercase) disables colors. |
| TestEnvironmentVariableEdgeCases | `test_search_dirs_removes_duplicates` | TASKFILE_HELP_SEARCH_DIRS removes duplicate directories. |
| TestEnvironmentVariableEdgeCases | `test_search_dirs_with_empty_entries` | TASKFILE_HELP_SEARCH_DIRS with empty entries filters them out. |
| TestEnvironmentVariablePriority | `test_cli_overrides_group_pattern_env` | Command-line --group-pattern overrides TASKFILE_HELP_GROUP_PATTERN. |
| TestEnvironmentVariablePriority | `test_cli_overrides_no_color_env` | Command-line --no-color flag takes precedence over NO_COLOR env var. |
| TestEnvironmentVariablePriority | `test_cli_overrides_search_dirs_env` | Command-line --search-dirs overrides TASKFILE_HELP_SEARCH_DIRS. |
| TestEnvironmentVariablePriority | `test_env_overrides_pyproject` | Environment variable overrides pyproject.toml. |
| TestEnvironmentVariablePriority | `test_no_color_takes_precedence_over_taskfile_help_no_color` | NO_COLOR takes precedence over TASKFILE_HELP_NO_COLOR. |
| TestEnvironmentVariables | `test_group_pattern_env_var` | TASKFILE_HELP_GROUP_PATTERN environment variable sets group pattern. |
| TestEnvironmentVariables | `test_group_pattern_env_var_not_set` | Missing TASKFILE_HELP_GROUP_PATTERN uses default pattern. |
| TestEnvironmentVariables | `test_no_color_env_var` | NO_COLOR environment variable disables colors. |
| TestEnvironmentVariables | `test_no_color_env_var_empty` | Empty NO_COLOR environment variable does not disable colors. |
| TestEnvironmentVariables | `test_search_dirs_env_var` | TASKFILE_HELP_SEARCH_DIRS environment variable sets search directories. |
| TestEnvironmentVariables | `test_search_dirs_env_var_empty` | Empty TASKFILE_HELP_SEARCH_DIRS defaults to current directory. |
| TestEnvironmentVariables | `test_search_dirs_env_var_single` | TASKFILE_HELP_SEARCH_DIRS with single directory. |
| TestEnvironmentVariables | `test_taskfile_help_no_color_false` | TASKFILE_HELP_NO_COLOR=false does not disable colors. |
| TestEnvironmentVariables | `test_taskfile_help_no_color_one` | TASKFILE_HELP_NO_COLOR=1 disables colors. |
| TestEnvironmentVariables | `test_taskfile_help_no_color_true` | TASKFILE_HELP_NO_COLOR=true disables colors. |
| TestEnvironmentVariables | `test_taskfile_help_no_color_yes` | TASKFILE_HELP_NO_COLOR=yes disables colors. |
| TestEnvironmentVariablesWithPyproject | `test_env_group_pattern_overrides_pyproject` | Environment TASKFILE_HELP_GROUP_PATTERN overrides pyproject.toml. |
| TestEnvironmentVariablesWithPyproject | `test_env_no_color_overrides_pyproject` | Environment NO_COLOR overrides pyproject.toml no-color setting. |
| TestEnvironmentVariablesWithPyproject | `test_pyproject_group_pattern_when_no_env` | pyproject.toml group-pattern is used when no environment variable is set. |
| TestEnvironmentVariablesWithPyproject | `test_pyproject_no_color_when_no_env` | pyproject.toml no-color is used when no environment variable is set. |
| TestEnvironmentVariablesWithPyproject | `test_pyproject_search_dirs_when_no_env` | pyproject.toml search-dirs is used when no environment variable is set. |
| TestExtractDescription | `test_description_with_extra_spaces` | Test description with extra spaces. |
| TestExtractDescription | `test_empty_description` | Test empty description. |
| TestExtractDescription | `test_non_desc_line` | Test non-description line. |
| TestExtractDescription | `test_task_line` | Test task definition line (should not match). |
| TestExtractDescription | `test_valid_description` | Test extraction of valid description. |
| TestExtractGroupName | `test_empty_line` | Test empty line. |
| TestExtractGroupName | `test_group_marker_with_extra_spaces` | Test group marker with extra spaces. |
| TestExtractGroupName | `test_no_group_marker` | Test line without group marker. |
| TestExtractGroupName | `test_task_line` | Test task definition line (should not match). |
| TestExtractGroupName | `test_valid_group_marker` | Test extraction of valid group marker. |
| TestExtractTaskName | `test_desc_line` | Test description line (should not match). |
| TestExtractTaskName | `test_invalid_indentation` | Test task with wrong indentation. |
| TestExtractTaskName | `test_task_with_hyphens` | Test task name with hyphens. |
| TestExtractTaskName | `test_task_with_namespace` | Test task name with namespace separator. |
| TestExtractTaskName | `test_task_with_underscores` | Test task name with underscores. |
| TestExtractTaskName | `test_valid_task_name` | Test extraction of valid task name. |
| TestGenerateCompletionScripts | `test_generate_bash_completion` | Test bash completion script generation. |
| TestGenerateCompletionScripts | `test_generate_fish_completion` | Test fish completion script generation. |
| TestGenerateCompletionScripts | `test_generate_ksh_completion` | Test ksh completion script generation. |
| TestGenerateCompletionScripts | `test_generate_tcsh_completion` | Test tcsh completion script generation. |
| TestGenerateCompletionScripts | `test_generate_zsh_completion` | Test zsh completion script generation. |
| TestGetCompletions | `test_complete_flags` | Test completing command-line flags. |
| TestGetCompletions | `test_complete_namespace_without_colon` | Test completing namespace names. |
| TestGetCompletions | `test_complete_task_name_with_colon` | Test completing task names within a namespace. |
| TestGetCompletions | `test_empty_word_returns_all_namespaces` | Test that empty word returns all available namespaces. |
| TestGetConfigFile | `test_get_config_file_custom_order` | Get config file with custom search order. |
| TestGetConfigFile | `test_get_config_file_no_config` | Get config file when no config files exist. |
| TestGetConfigFile | `test_get_config_file_only_taskfile_help_yml` | Get config file when only taskfile_help.yml exists. |
| TestGetConfigFile | `test_get_config_file_pyproject_toml_fallback` | Get config file when only pyproject.toml exists. |
| TestGetConfigFile | `test_get_config_file_taskfile_help_yml_first` | Get config file when taskfile_help.yml exists (takes precedence). |
| TestInstallCompletion | `test_auto_detect_shell_from_environment` | Test auto-detecting shell from $SHELL environment variable. |
| TestInstallCompletion | `test_creates_parent_directories` | Test that parent directories are created if they don't exist. |
| TestInstallCompletion | `test_fails_for_unsupported_shell` | Test failure for unsupported shell. |
| TestInstallCompletion | `test_fails_when_path_is_readonly` | Test that installation fails gracefully when path is read-only. |
| TestInstallCompletion | `test_fails_when_shell_cannot_be_detected` | Test failure when shell cannot be auto-detected. |
| TestInstallCompletion | `test_handles_csh_as_tcsh` | Test that csh is handled as tcsh. |
| TestInstallCompletion | `test_installs_bash_completion` | Test installing bash completion script. |
| TestInstallCompletion | `test_installs_fish_completion` | Test installing fish completion script. |
| TestInstallCompletion | `test_installs_ksh_completion` | Test installing ksh completion script. |
| TestInstallCompletion | `test_installs_tcsh_completion` | Test installing tcsh completion script. |
| TestInstallCompletion | `test_installs_zsh_completion` | Test installing zsh completion script. |
| TestInstallCompletion | `test_overwrites_existing_completion_script` | Test that existing completion script is overwritten. |
| TestInstallCompletion | `test_unsupported_shell_in_sourcing_instructions` | Test that \_get_sourcing_instructions handles unsupported shells gracefully. |
| TestIntegration | `test_complete_workflow_bash` | Test complete workflow: discover, complete, generate. |
| TestIntegration | `test_partial_namespace_completion` | Test partial namespace completion. |
| TestIntegration | `test_partial_task_completion` | Test partial task name completion. |
| TestIsInternalTask | `test_empty_line` | Test empty line. |
| TestIsInternalTask | `test_internal_false` | Test internal: false flag. |
| TestIsInternalTask | `test_internal_true` | Test internal: true flag. |
| TestIsInternalTask | `test_non_internal_line` | Test non-internal line. |
| TestJsonOutputter | `test_output_all` | Test outputting all taskfiles in JSON format. |
| TestJsonOutputter | `test_output_empty_tasks` | Test outputting empty task list in JSON. |
| TestJsonOutputter | `test_output_error` | Test outputting an error in JSON format. |
| TestJsonOutputter | `test_output_heading` | Test outputting a heading in JSON format. |
| TestJsonOutputter | `test_output_message` | Test outputting a message in JSON format. |
| TestJsonOutputter | `test_output_search_results_empty` | Test outputting empty search results in JSON. |
| TestJsonOutputter | `test_output_search_results_main_namespace` | Test outputting search results for main namespace in JSON. |
| TestJsonOutputter | `test_output_search_results_match_types` | Test outputting search results with different match types. |
| TestJsonOutputter | `test_output_search_results_with_results` | Test outputting search results in JSON format. |
| TestJsonOutputter | `test_output_single_main_namespace` | Test outputting tasks for main namespace in JSON. |
| TestJsonOutputter | `test_output_single_with_tasks` | Test outputting tasks in JSON format. |
| TestJsonOutputter | `test_output_warning` | Test outputting a warning in JSON format. |
| TestMain | `test_main_all_with_no_taskfiles` | Test main 'all' namespace when no taskfiles exist. |
| TestMain | `test_main_colors_disabled_for_json` | Test colors are disabled for JSON output. |
| TestMain | `test_main_namespace_main_alias` | Test 'main' namespace is treated as main taskfile. |
| TestMain | `test_main_namespace_not_found` | Test main when namespace taskfile is not found. |
| TestMain | `test_main_taskfile_not_found` | Test main when taskfile is not found. |
| TestMain | `test_main_with_all_namespace` | Test main with 'all' namespace. |
| TestMain | `test_main_with_empty_taskfile` | Test main with empty taskfile. |
| TestMain | `test_main_with_internal_tasks_only` | Test main with taskfile containing only internal tasks. |
| TestMain | `test_main_with_json_output` | Test main with JSON output. |
| TestMain | `test_main_with_main_taskfile` | Test main with a main taskfile. |
| TestMain | `test_main_with_multiple_namespaces` | Test main 'all' namespace with multiple namespace taskfiles. |
| TestMain | `test_main_with_namespace` | Test main with a namespace taskfile. |
| TestMain | `test_main_with_no_color` | Test main with --no-color flag. |
| TestMain | `test_main_with_search_dirs` | Test main with custom search directories. |
| TestMain | `test_main_with_verbose` | Test main with verbose output. |
| TestMainEdgeCases | `test_main_all_namespace_shows_everything` | Test 'all' namespace shows all taskfiles. |
| TestMainEdgeCases | `test_main_colors_disabled_for_json` | Test colors are disabled for JSON output even with TTY. |
| TestMainEdgeCases | `test_main_empty_taskfile_with_all` | Test 'all' namespace with empty taskfile. |
| TestMainEdgeCases | `test_main_verbose_with_json_suppressed` | Test verbose output is suppressed with JSON. |
| TestMatchingFunctions | `test_matches_all_patterns_case_insensitive` | Test case-insensitive matching with multiple patterns. |
| TestMatchingFunctions | `test_matches_all_patterns_multiple` | Test matching with multiple patterns (AND logic). |
| TestMatchingFunctions | `test_matches_all_patterns_no_match` | Test when not all patterns match. |
| TestMatchingFunctions | `test_matches_all_patterns_single` | Test matching with a single pattern. |
| TestMatchingFunctions | `test_matches_all_regexes` | Test matching multiple regexes. |
| TestMatchingFunctions | `test_matches_all_regexes_no_match` | Test when not all regexes match. |
| TestMatchingFunctions | `test_matches_regex_basic` | Test basic regex matching. |
| TestMatchingFunctions | `test_matches_regex_invalid` | Test invalid regex returns False. |
| TestMatchingFunctions | `test_matches_regex_no_match` | Test regex not matching. |
| TestOutputEdgeCases | `test_text_outputter_error_message` | Test error message output. |
| TestOutputEdgeCases | `test_text_outputter_heading_message` | Test heading message output. |
| TestOutputEdgeCases | `test_text_outputter_plain_message` | Test plain message output. |
| TestOutputEdgeCases | `test_text_outputter_warning_message` | Test warning message output. |
| TestParseTaskfile | `test_parse_empty_taskfile` | Test parsing an empty taskfile. |
| TestParseTaskfile | `test_parse_nonexistent_file` | Test parsing a non-existent file. |
| TestParseTaskfile | `test_parse_simple_taskfile` | Test parsing a simple taskfile. |
| TestParseTaskfile | `test_parse_taskfile_preserves_order` | Test that parsing preserves task order. |
| TestParseTaskfile | `test_parse_taskfile_with_groups` | Test parsing a taskfile with group markers. |
| TestParseTaskfile | `test_parse_taskfile_with_internal_tasks` | Test parsing a taskfile with internal tasks. |
| TestParseTaskfile | `test_parse_taskfile_with_unicode` | Test parsing a taskfile with unicode characters. |
| TestParseTaskfile | `test_parse_taskfile_without_descriptions` | Test parsing a taskfile where tasks lack descriptions. |
| TestParseTaskfile | `test_parse_taskfile_without_tasks_section` | Test parsing a taskfile without tasks section. |
| TestParserEdgeCases | `test_parse_file_permission_denied` | Test parsing a file without read permissions. |
| TestParserEdgeCases | `test_parse_file_with_encoding_error` | Test parsing a file with invalid encoding. |
| TestParserEdgeCases | `test_parse_taskfile_desc_before_task` | Test desc appearing before any task definition. |
| TestParserEdgeCases | `test_parse_taskfile_internal_before_desc` | Test internal flag appearing before desc. |
| TestParserEdgeCases | `test_parse_taskfile_multiple_desc_lines` | Test task with multiple desc lines (last one wins). |
| TestPyProjectConfigFile | `test_load_config_invalid_toml` | Load config with invalid TOML. |
| TestPyProjectConfigFile | `test_load_config_no_file` | Load config when pyproject.toml doesn't exist. |
| TestPyProjectConfigFile | `test_load_config_no_tool_section` | Load config when tool section doesn't exist. |
| TestPyProjectConfigFile | `test_load_config_with_group_pattern` | Load config with group-pattern from pyproject.toml. |
| TestPyProjectConfigFile | `test_load_config_with_no_color` | Load config with no-color setting from pyproject.toml. |
| TestPyProjectConfigFile | `test_load_config_with_search_dirs` | Load config with search-dirs from pyproject.toml. |
| TestSaveTaskIfValid | `test_internal_task_not_saved` | Test that internal tasks are not saved. |
| TestSaveTaskIfValid | `test_multiple_tasks` | Test saving multiple tasks. |
| TestSaveTaskIfValid | `test_task_without_description_not_saved` | Test that tasks without descriptions are not saved. |
| TestSaveTaskIfValid | `test_task_without_name_not_saved` | Test that tasks without names are not saved. |
| TestSaveTaskIfValid | `test_valid_public_task` | Test saving a valid public task. |
| TestSearchTaskfiles | `test_search_empty_taskfiles` | Test search with empty taskfiles list. |
| TestSearchTaskfiles | `test_search_no_filters` | Test search with no filters returns empty. |
| TestSearchTaskfiles | `test_search_no_matches` | Test search with no matching results. |
| TestSearchTaskfiles | `test_search_with_multiple_patterns` | Test search with multiple patterns (AND logic). |
| TestSearchTaskfiles | `test_search_with_multiple_regexes` | Test search with multiple regexes. |
| TestSearchTaskfiles | `test_search_with_patterns_across_fields` | Test search with patterns matching across different fields. |
| TestSearchTaskfiles | `test_search_with_patterns_and_regexes` | Test search with both patterns and regexes. |
| TestSearchTaskfiles | `test_search_with_single_pattern` | Test search with a single pattern. |
| TestSearchTaskfiles | `test_search_with_single_regex` | Test search with a single regex. |
| TestTaskMatchesFilters | `test_task_matches_multiple_patterns` | Test task matching with multiple patterns (AND logic). |
| TestTaskMatchesFilters | `test_task_matches_multiple_regexes` | Test task matching with multiple regexes. |
| TestTaskMatchesFilters | `test_task_matches_patterns_across_fields` | Test patterns matching across different fields. |
| TestTaskMatchesFilters | `test_task_matches_patterns_and_regexes` | Test task matching with both patterns and regexes. |
| TestTaskMatchesFilters | `test_task_matches_single_pattern` | Test task matching with a single pattern. |
| TestTaskMatchesFilters | `test_task_matches_single_regex` | Test task matching with a single regex. |
| TestTaskMatchesFilters | `test_task_no_match_patterns` | Test task not matching when patterns don't all match. |
| TestTaskfileDiscovery | `test_find_main_taskfile_lowercase_yaml` | Test finding lowercase taskfile.yaml. |
| TestTaskfileDiscovery | `test_find_main_taskfile_lowercase_yml` | Test finding lowercase taskfile.yml. |
| TestTaskfileDiscovery | `test_find_main_taskfile_multiple_dirs` | Test finding main taskfile in multiple directories. |
| TestTaskfileDiscovery | `test_find_main_taskfile_not_found` | Test when main taskfile is not found. |
| TestTaskfileDiscovery | `test_find_main_taskfile_prefers_uppercase` | Test uppercase Taskfile is preferred over lowercase. |
| TestTaskfileDiscovery | `test_find_main_taskfile_prefers_yml` | Test .yml extension is preferred over .yaml. |
| TestTaskfileDiscovery | `test_find_main_taskfile_yaml` | Test finding main Taskfile.yaml. |
| TestTaskfileDiscovery | `test_find_main_taskfile_yml` | Test finding main Taskfile.yml. |
| TestTaskfileDiscovery | `test_find_namespace_taskfile_hyphen` | Test finding namespace taskfile with hyphen separator. |
| TestTaskfileDiscovery | `test_find_namespace_taskfile_not_found` | Test when namespace taskfile is not found. |
| TestTaskfileDiscovery | `test_find_namespace_taskfile_underscore` | Test finding namespace taskfile with underscore separator. |
| TestTaskfileDiscovery | `test_find_namespace_taskfile_yaml_extension` | Test finding namespace taskfile with .yaml extension. |
| TestTaskfileDiscovery | `test_get_all_namespace_taskfiles` | Test getting all namespace taskfiles. |
| TestTaskfileDiscovery | `test_get_all_namespace_taskfiles_empty` | Test getting namespace taskfiles when none exist. |
| TestTaskfileDiscovery | `test_get_all_namespace_taskfiles_ignores_main` | Test main taskfile is excluded from namespace list. |
| TestTaskfileDiscovery | `test_get_all_namespace_taskfiles_removes_duplicates` | Test duplicate namespaces are removed. |
| TestTaskfileDiscovery | `test_get_all_namespace_taskfiles_sorted` | Test namespace taskfiles are sorted alphabetically. |
| TestTaskfileDiscovery | `test_get_possible_paths_empty_namespace` | Test getting possible paths for empty namespace. |
| TestTaskfileDiscovery | `test_get_possible_paths_main` | Test getting possible paths for main taskfile. |
| TestTaskfileDiscovery | `test_get_possible_paths_multiple_dirs` | Test getting possible paths across multiple directories. |
| TestTaskfileDiscovery | `test_get_possible_paths_namespace` | Test getting possible paths for a namespace. |
| TestTaskfileDiscovery | `test_handles_nonexistent_search_dir` | Test nonexistent search directories are handled gracefully. |
| TestTaskfileDiscovery | `test_ignores_directories` | Test directories matching the pattern are ignored. |
| TestTaskfileDiscovery | `test_ignores_empty_namespace` | Test files with empty namespace are ignored. |
| TestTaskfileDiscovery | `test_ignores_wrong_extension` | Test files with wrong extensions are ignored. |
| TestTaskfileDiscovery | `test_ignores_wrong_prefix` | Test files with wrong prefix are ignored. |
| TestTaskfileDiscovery | `test_lowercase_taskfile_prefix` | Test lowercase 'taskfile' prefix is recognized. |
| TestTaskfileDiscovery | `test_mixed_case_taskfile_prefix` | Test mixed case 'Taskfile' prefix is recognized. |
| TestTaskfileDiscovery | `test_multiple_namespaces_mixed_separators` | Test multiple namespaces with mixed separators and extensions. |
| TestTaskfileDiscovery | `test_namespace_with_numbers` | Test namespace with numbers in the name. |
| TestTaskfileDiscovery | `test_namespace_with_underscores` | Test namespace with underscores in the name. |
| TestTaskfileDiscovery | `test_search_dirs_order_matters` | Test search directory order determines precedence (first match wins). |
| TestTaskfileHelpConfigFile | `test_load_config_empty_file` | Load config from empty taskfile_help.yml. |
| TestTaskfileHelpConfigFile | `test_load_config_invalid_yaml` | Load config with invalid YAML. |
| TestTaskfileHelpConfigFile | `test_load_config_no_file` | Load config when taskfile_help.yml doesn't exist. |
| TestTaskfileHelpConfigFile | `test_load_config_with_all_settings` | Load config with all supported settings from taskfile_help.yml. |
| TestTaskfileHelpConfigFile | `test_load_config_with_group_pattern` | Load config with group-pattern from taskfile_help.yml. |
| TestTaskfileHelpConfigFile | `test_load_config_with_no_color` | Load config with no-color setting from taskfile_help.yml. |
| TestTaskfileHelpConfigFile | `test_load_config_with_search_dirs` | Load config with search-dirs from taskfile_help.yml. |
| TestTextOutputter | `test_output_all` | Test outputting all taskfiles. |
| TestTextOutputter | `test_output_error` | Test outputting an error message. |
| TestTextOutputter | `test_output_heading` | Test outputting a heading. |
| TestTextOutputter | `test_output_message` | Test outputting a message. |
| TestTextOutputter | `test_output_search_results_main_namespace` | Test outputting search results for main namespace. |
| TestTextOutputter | `test_output_search_results_multiple_groups` | Test outputting search results with multiple groups in same namespace. |
| TestTextOutputter | `test_output_search_results_no_results` | Test outputting search results when no tasks match. |
| TestTextOutputter | `test_output_search_results_with_results` | Test outputting search results with matching tasks. |
| TestTextOutputter | `test_output_single_main_namespace` | Test outputting tasks for main namespace (empty string). |
| TestTextOutputter | `test_output_single_no_tasks` | Test outputting when no tasks exist. |
| TestTextOutputter | `test_output_single_with_tasks` | Test outputting tasks for a single namespace. |
| TestTextOutputter | `test_output_warning` | Test outputting a warning message. |
| TestValidateTaskfile | `test_empty_file` | Test warning when file is empty. |
| TestValidateTaskfile | `test_invalid_yaml_syntax` | Test warning when YAML has syntax errors. |
| TestValidateTaskfile | `test_missing_tasks_section` | Test warning when tasks section is missing. |
| TestValidateTaskfile | `test_missing_version_field` | Test warning when version field is missing. |
| TestValidateTaskfile | `test_multiple_validation_errors` | Test multiple validation errors are reported. |
| TestValidateTaskfile | `test_root_is_list` | Test warning when root is a list instead of dictionary. |
| TestValidateTaskfile | `test_task_cmds_is_dict` | Test warning when task cmds is a dict instead of list or string. |
| TestValidateTaskfile | `test_task_deps_is_string` | Test warning when task deps is a string instead of list. |
| TestValidateTaskfile | `test_task_desc_is_number` | Test warning when task desc is a number instead of string. |
| TestValidateTaskfile | `test_task_internal_is_string` | Test warning when task internal is a string instead of boolean. |
| TestValidateTaskfile | `test_task_is_string` | Test warning when task definition is a string instead of dict. |
| TestValidateTaskfile | `test_tasks_is_list` | Test warning when tasks is a list instead of dictionary. |
| TestValidateTaskfile | `test_tasks_is_string` | Test warning when tasks is a string instead of dictionary. |
| TestValidateTaskfile | `test_valid_taskfile_passes` | Test valid Taskfile passes validation. |
| TestValidateTaskfile | `test_valid_taskfile_with_optional_fields` | Test valid optional fields produce no warnings. |
| TestValidateTaskfile | `test_wrong_version_float` | Test warning when version is '3.0' instead of '3'. |
| TestValidateTaskfile | `test_wrong_version_number` | Test warning when version is a number instead of string. |
| TestValidateTaskfile | `test_wrong_version_string` | Test warning when version is '2' instead of '3'. |

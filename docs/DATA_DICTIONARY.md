# Complete variable dictionary

This document is generated from `configs/semantic_annotations.json` and the immutable source workbooks.
The authoritative machine-readable version is `data/metadata/data_dictionary.csv`.
Observed free-text and identifier values are intentionally suppressed.

## Status vocabulary

- `confirmed_*`: supported by a repository description, related publication, source document, or self-describing survey header.
- `derived_and_empirically_verified`: formula reproduced for every deposited row.
- `partially_verified_rounding_unresolved`: construct is known but deposited rounding is not exactly reproducible.
- `coding_not_deposited`: construct is known but numeric code labels are missing.
- `needs_author_confirmation`: a specific semantic claim would require depositor confirmation.

## D1: BMI_Depression

| # | Variable | Privacy role | Meaning | Coding/unit | Semantic status |
|---:|---|---|---|---|---|
| 1 | `Age` | quasi_identifier | Participant age band. | 18-30; 31-40; 41-50; 51-60 years | confirmed_column_header |
| 2 | `Gender` | quasi_identifier | Self-reported gender. |  | confirmed_column_header |
| 3 | `Marital status` | quasi_identifier | Self-reported marital-status category. |  | confirmed_column_header |
| 4 | `Nationality` | other | Participant nationality; constant Saudi in the deposited analytic file. |  | confirmed_column_header |
| 5 | `Region` | quasi_identifier | Saudi administrative region grouped as western, southern, eastern, northern, or central. |  | confirmed_column_header |
| 6 | `Educational level` | quasi_identifier | Highest reported educational-level category. |  | confirmed_column_header |
| 7 | `Occupation` | quasi_identifier | Reported employment or activity category. |  | confirmed_column_header |
| 8 | `Family income per month` | quasi_identifier | Monthly household income band in Saudi riyals. | SAR/month | confirmed_column_header |
| 9 | `Weight/kg` | quasi_identifier | Self-reported body weight. | kg | confirmed_column_header |
| 10 | `Hight/cm` | quasi_identifier | Self-reported height; source column retains the misspelling 'Hight'. | cm | confirmed_column_header |
| 11 | `BMI` | sensitive | Body mass index computed as weight in kilograms divided by squared height in metres. | kg/m^2 | confirmed_column_header |
| 12 | `Do you smoke?` | quasi_identifier;sensitive | Current or former smoking-status category. |  | confirmed_column_header |
| 13 | `Do you have chronic diseases?` | sensitive | Reported physician-diagnosed chronic-disease category or combination. |  | confirmed_column_header |
| 14 | `Q 1` | item_level | Beck Depression Inventory-II response score for item 1; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 15 | `Q 2` | item_level | Beck Depression Inventory-II response score for item 2; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 16 | `Q 3` | item_level | Beck Depression Inventory-II response score for item 3; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 17 | `Q 4` | item_level | Beck Depression Inventory-II response score for item 4; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 18 | `Q 5` | item_level | Beck Depression Inventory-II response score for item 5; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 19 | `Q 6` | item_level | Beck Depression Inventory-II response score for item 6; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 20 | `Q 7` | item_level | Beck Depression Inventory-II response score for item 7; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 21 | `Q 8` | item_level | Beck Depression Inventory-II response score for item 8; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 22 | `Q 9` | item_level | Beck Depression Inventory-II response score for item 9; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 23 | `Q 10` | item_level | Beck Depression Inventory-II response score for item 10; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 24 | `Q 11` | item_level | Beck Depression Inventory-II response score for item 11; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 25 | `Q 12` | item_level | Beck Depression Inventory-II response score for item 12; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 26 | `Q 13` | item_level | Beck Depression Inventory-II response score for item 13; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 27 | `Q 14` | item_level | Beck Depression Inventory-II response score for item 14; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 28 | `Q 15` | item_level | Beck Depression Inventory-II response score for item 15; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 29 | `Q 16` | item_level | Beck Depression Inventory-II response score for item 16; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 30 | `Q 17` | item_level | Beck Depression Inventory-II response score for item 17; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 31 | `Q 18` | item_level | Beck Depression Inventory-II response score for item 18; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 32 | `Q 19` | item_level | Beck Depression Inventory-II response score for item 19; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 33 | `Q 20` | item_level | Beck Depression Inventory-II response score for item 20; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 34 | `Q 21` | item_level | Beck Depression Inventory-II response score for item 21; item wording is not reproduced in the repository workbook. | 0=no symptom to 3=severe symptom; 0-3 points | confirmed_repository_description |
| 35 | `Depression score` | sensitive | Sum of the 21 Beck Depression Inventory-II item scores; higher values represent more severe symptoms. | sum(Q1..Q21); 0-63 points | derived_and_empirically_verified |

## D2: GLP1

| # | Variable | Privacy role | Meaning | Coding/unit | Semantic status |
|---:|---|---|---|---|---|
| 1 | `Timestamp` | structural_identifier | Survey submission timestamp. Treated conservatively as a direct/operational identifier because it is record-unique. |  | confirmed_column_header |
| 2 | `Do you agree to participate in the survey?` | other | Do you agree to participate in the survey? |  | confirmed_column_header |
| 3 | `Researcher's number` | structural_identifier | Operational researcher or collector code. Treated conservatively as an identifier-like field despite low cardinality. |  | confirmed_column_header |
| 4 | `Age` | quasi_identifier | Participant age band. |  | confirmed_column_header |
| 5 | `Sex` | quasi_identifier | Self-reported sex category. |  | confirmed_column_header |
| 6 | `Weight` | quasi_identifier | Self-reported body-weight band. | kg | confirmed_column_header |
| 7 | `Height` | quasi_identifier | Self-reported height band. | cm | confirmed_column_header |
| 8 | `Marital status` | quasi_identifier | Self-reported marital-status category. |  | confirmed_column_header |
| 9 | `Educational status` | quasi_identifier | Educational status |  | confirmed_column_header |
| 10 | `Job status` | quasi_identifier | Employment or activity-status category. |  | confirmed_column_header |
| 11 | `Do you have health insurance?` | quasi_identifier | Do you have health insurance? |  | confirmed_column_header |
| 12 | `monthly income` | quasi_identifier | Monthly income band in Saudi riyals. | SAR/month | confirmed_column_header |
| 13 | `Do you suffer from any chronic illness?` | sensitive | Do you suffer from any chronic illness? |  | confirmed_column_header |
| 14 | `City` | quasi_identifier | Reported city category. Several English labels and spreadsheet-error tokens require depositor confirmation before substantive analysis. |  | needs_author_confirmation |
| 15 | `Did you know that it is possible to use some diabetes medications for weight loss?` | other | Did you know that it is possible to use some diabetes medications for weight loss? |  | confirmed_column_header |
| 16 | `If the answer is yes, which of these medications can be used? More than one answer can be selected.` | other | If the answer is yes, which of these medications can be used? More than one answer can be selected. |  | confirmed_column_header |
| 17 | `Which of the following medications is approved for weight loss by regulatory bodies, such as the U.S. Food and Drug Administration (FDA)? You can select more than one answer.` | other | Which of the following medications is approved for weight loss by regulatory bodies, such as the U.S. Food and Drug Administration (FDA)? You can select more than one answer. |  | confirmed_column_header |
| 18 | `What are the side effects of these medications? You can choose more than one.` | other | What are the side effects of these medications? You can choose more than one. |  | confirmed_column_header |
| 19 | `What is the source of your information regarding the effectiveness of these medications in weight loss?` | other | What is the source of your information regarding the effectiveness of these medications in weight loss? |  | confirmed_column_header |
| 20 | `There is sufficient oversight from the relevant authorities regarding the dispensing of diabetes medications used for weight loss.` | other | There is sufficient oversight from the relevant authorities regarding the dispensing of diabetes medications used for weight loss. |  | confirmed_column_header |
| 21 | `These medications can be used for weight loss, but only under medical supervision.` | item_level | These medications can be used for weight loss, but only under medical supervision. |  | confirmed_column_header |
| 22 | `Using these medications is the first and best option for weight loss.` | other | Using these medications is the first and best option for weight loss. |  | confirmed_column_header |
| 23 | `These medications help you make the necessary lifestyle changes to lose weight and improve your health.` | item_level | These medications help you make the necessary lifestyle changes to lose weight and improve your health. |  | confirmed_column_header |
| 24 | `These medications are considered safe and can be used without complications.` | item_level | These medications are considered safe and can be used without complications. |  | confirmed_column_header |
| 25 | `The effectiveness of these medications in weight loss is guaranteed.` | other | The effectiveness of these medications in weight loss is guaranteed. |  | confirmed_column_header |
| 26 | `The long-lasting effectiveness of these drugs` | other | The long-lasting effectiveness of these drugs |  | confirmed_column_header |
| 27 | `Have you used any weight loss medications in the past twelve months?` | sensitive | Have you used any weight loss medications in the past twelve months? |  | confirmed_column_header |
| 28 | `Which of the following diabetes medications did you use to lose weight?` | other | Which of the following diabetes medications did you use to lose weight? |  | confirmed_column_header |
| 29 | `What other methods do you usually use to lose weight besides diabetes medication?` | other | What other methods do you usually use to lose weight besides diabetes medication? |  | confirmed_column_header |
| 30 | `Where do you get these medicines?` | other | Where do you get these medicines? |  | confirmed_column_header |
| 31 | `Have you had difficulty obtaining these medications recently?` | other | Have you had difficulty obtaining these medications recently? |  | confirmed_column_header |
| 32 | `If you have previously used these medications, how much weight (kg) did you lose?` | other | If you have previously used these medications, how much weight (kg) did you lose? |  | confirmed_column_header |
| 33 | `Do you check the source of these medicines when you buy them?` | other | Do you check the source of these medicines when you buy them? |  | confirmed_column_header |
| 34 | `Did you consult a doctor before using these medications?` | other | Did you consult a doctor before using these medications? |  | confirmed_column_header |
| 35 | `Did you regain your weight after stopping using it?` | other | Did you regain your weight after stopping using it? |  | confirmed_column_header |
| 36 | `Have you experienced any side effects when using these medications?` | sensitive | Have you experienced any side effects when using these medications? |  | confirmed_column_header |
| 37 | `Do you read the medical information about products used for weight loss?` | other | Do you read the medical information about products used for weight loss? |  | confirmed_column_header |
| 38 | `Any comments, suggestions, or weight loss experiences?` | free_text | Optional free-text comment on weight-loss experience. Values must never be quoted or redistributed by this project. |  | confirmed_column_header |

## D3: Health_Message

| # | Variable | Privacy role | Meaning | Coding/unit | Semantic status |
|---:|---|---|---|---|---|
| 1 | `ID` | structural_identifier | Deposited participant record identifier. |  | confirmed_column_header |
| 2 | `Age` | quasi_identifier | Participant age in years. | years | confirmed_repository_description |
| 3 | `Gender` | quasi_identifier | Coded participant gender; code-to-label mapping is not present in the local workbook. |  | coding_not_deposited |
| 4 | `Nationality` | quasi_identifier | Coded nationality category; code-to-label mapping is not present in the local workbook. |  | coding_not_deposited |
| 5 | `Education_Level` | quasi_identifier | Coded latest educational qualification; code-to-label mapping is not present in the local workbook. |  | coding_not_deposited |
| 6 | `City` | quasi_identifier | Coded Saudi city of residence; code-to-label mapping is not present in the local workbook. |  | coding_not_deposited |
| 7 | `P2_1` | item_level | Deposited depression-instrument item score P2 item 1; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 8 | `P2_2` | item_level | Deposited depression-instrument item score P2 item 2; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 9 | `P2_3` | item_level | Deposited depression-instrument item score P2 item 3; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 10 | `P2_4` | item_level | Deposited depression-instrument item score P2 item 4; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 11 | `P2_5` | item_level | Deposited depression-instrument item score P2 item 5; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 12 | `P2_6` | item_level | Deposited depression-instrument item score P2 item 6; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 13 | `P2_7` | item_level | Deposited depression-instrument item score P2 item 7; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 14 | `P2_8` | item_level | Deposited depression-instrument item score P2 item 8; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 15 | `P2_9` | item_level | Deposited depression-instrument item score P2 item 9; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 16 | `P2_10` | item_level | Deposited depression-instrument item score P2 item 10; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 17 | `P2_11` | item_level | Deposited depression-instrument item score P2 item 11; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 18 | `P2_12` | item_level | Deposited depression-instrument item score P2 item 12; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 19 | `P2_13` | item_level | Deposited depression-instrument item score P2 item 13; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 20 | `P2_14` | item_level | Deposited depression-instrument item score P2 item 14; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 21 | `P2_15` | item_level | Deposited depression-instrument item score P2 item 15; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 22 | `P2_16` | item_level | Deposited depression-instrument item score P2 item 16; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 23 | `P2_17` | item_level | Deposited depression-instrument item score P2 item 17; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 24 | `P2_18` | item_level | Deposited depression-instrument item score P2 item 18; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 25 | `P2_19` | item_level | Deposited depression-instrument item score P2 item 19; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 26 | `P2_20` | item_level | Deposited depression-instrument item score P2 item 20; exact item-to-question mapping is not included in the local deposit. | 0-3 points | coding_not_deposited |
| 27 | `P2_T` | item_level;sensitive | Total depression-instrument score across P2_1 to P2_20 as deposited; the sum is verified, but the related publication describes BDI-II and the workbook contains only 20 visible P2 item columns, which requires author confirmation. | points | needs_author_confirmation |
| 28 | `P3_1` | item_level | State Anxiety Inventory item 1 response score. | 1-4 points | confirmed_repository_description |
| 29 | `P3_2` | item_level | State Anxiety Inventory item 2 response score. | 1-4 points | confirmed_repository_description |
| 30 | `P3_3` | item_level | State Anxiety Inventory item 3 response score. | 1-4 points | confirmed_repository_description |
| 31 | `P3_4` | item_level | State Anxiety Inventory item 4 response score. | 1-4 points | confirmed_repository_description |
| 32 | `P3_5` | item_level | State Anxiety Inventory item 5 response score. | 1-4 points | confirmed_repository_description |
| 33 | `P3_6` | item_level | State Anxiety Inventory item 6 response score. | 1-4 points | confirmed_repository_description |
| 34 | `P3_7` | item_level | State Anxiety Inventory item 7 response score. | 1-4 points | confirmed_repository_description |
| 35 | `P3_8` | item_level | State Anxiety Inventory item 8 response score. | 1-4 points | confirmed_repository_description |
| 36 | `P3_9` | item_level | State Anxiety Inventory item 9 response score. | 1-4 points | confirmed_repository_description |
| 37 | `P3_10` | item_level | State Anxiety Inventory item 10 response score. | 1-4 points | confirmed_repository_description |
| 38 | `P3_11` | item_level | State Anxiety Inventory item 11 response score. | 1-4 points | confirmed_repository_description |
| 39 | `P3_12` | item_level | State Anxiety Inventory item 12 response score. | 1-4 points | confirmed_repository_description |
| 40 | `P3_13` | item_level | State Anxiety Inventory item 13 response score. | 1-4 points | confirmed_repository_description |
| 41 | `P3_14` | item_level | State Anxiety Inventory item 14 response score. | 1-4 points | confirmed_repository_description |
| 42 | `P3_15` | item_level | State Anxiety Inventory item 15 response score. | 1-4 points | confirmed_repository_description |
| 43 | `P3_16` | item_level | State Anxiety Inventory item 16 response score. | 1-4 points | confirmed_repository_description |
| 44 | `P3_17` | item_level | State Anxiety Inventory item 17 response score. | 1-4 points | confirmed_repository_description |
| 45 | `P3_18` | item_level | State Anxiety Inventory item 18 response score. | 1-4 points | confirmed_repository_description |
| 46 | `P3_19` | item_level | State Anxiety Inventory item 19 response score. | 1-4 points | confirmed_repository_description |
| 47 | `P3_20` | item_level | State Anxiety Inventory item 20 response score. | 1-4 points | confirmed_repository_description |
| 48 | `P3_T` | item_level;sensitive | Total state-anxiety score across the 20 P3 items. | points | derived_and_empirically_verified |
| 49 | `P4LS_GD` | other | Mean affect rating for G-framed, LS-severity messages with D outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 50 | `P4LS_GUD` | other | Mean affect rating for G-framed, LS-severity messages with UD outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 51 | `P4LS_LD` | other | Mean affect rating for L-framed, LS-severity messages with D outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 52 | `P4LS_LUD` | other | Mean affect rating for L-framed, LS-severity messages with UD outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 53 | `P4MS_GD` | other | Mean affect rating for G-framed, MS-severity messages with D outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 54 | `P4MS_GUD` | other | Mean affect rating for G-framed, MS-severity messages with UD outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 55 | `P4MS_LD` | other | Mean affect rating for L-framed, MS-severity messages with D outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 56 | `P4MS_LUD` | other | Mean affect rating for L-framed, MS-severity messages with UD outcomes (LS=less severe, MS=more severe, G=gain, L=loss, D=desirable, UD=undesirable). | 1-6 rating | confirmed_repository_description |
| 57 | `Age_Group` | other | Three-level derived age group (young, middle-aged, old); numeric code-to-label mapping is not deposited locally. |  | coding_not_deposited |
| 58 | `Gain_LS` | other | Mean affect rating for gain-framed, less-severe messages across desirable and undesirable outcomes. | 1-6 rating | derived_and_empirically_verified |
| 59 | `Loss_LS` | other | Mean affect rating for loss-framed, less-severe messages across desirable and undesirable outcomes. | 1-6 rating | derived_and_empirically_verified |
| 60 | `Gain_MS` | other | Mean affect rating for gain-framed, more-severe messages across desirable and undesirable outcomes. | 1-6 rating | derived_and_empirically_verified |
| 61 | `Loss_MS` | other | Mean affect rating for loss-framed, more-severe messages across desirable and undesirable outcomes. | 1-6 rating | derived_and_empirically_verified |
| 62 | `Gain` | other | Overall gain-frame affect score. Construct is confirmed, but the deposited rounding differs by up to 0.05 from the visible four-component mean. | 1-6 rating | partially_verified_rounding_unresolved |
| 63 | `Loss` | other | Overall loss-frame affect score. Construct is confirmed, but the deposited rounding differs by up to 0.05 from the visible four-component mean. | 1-6 rating | partially_verified_rounding_unresolved |
| 64 | `Gain_D` | other | Mean gain-frame affect rating for desirable outcomes across severity levels. | 1-6 rating | derived_and_empirically_verified |
| 65 | `Gain_UD` | other | Mean gain-frame affect rating for undesirable outcomes across severity levels. | 1-6 rating | derived_and_empirically_verified |
| 66 | `Loss_D` | other | Mean loss-frame affect rating for desirable outcomes across severity levels. | 1-6 rating | derived_and_empirically_verified |
| 67 | `Loss_UD` | other | Mean loss-frame affect rating for undesirable outcomes across severity levels. | 1-6 rating | derived_and_empirically_verified |

## D4: Employee_Attrition

| # | Variable | Privacy role | Meaning | Coding/unit | Semantic status |
|---:|---|---|---|---|---|
| 1 | `ID` | structural_identifier | Deposited employee-response record identifier. |  | confirmed_source_document |
| 2 | `Attrition` | sensitive | Whether the respondent had left a previous organization before the current job. | Yes/No | confirmed_source_document |
| 3 | `Gender` | quasi_identifier | Self-reported gender. | Male/Female | confirmed_source_document |
| 4 | `Age` | quasi_identifier | Participant age band. | 21-30; 31-40; 41-50; 51-60 years | confirmed_source_document |
| 5 | `Maritalstatus` | quasi_identifier | Self-reported marital status. | Single; Married; Divorced | confirmed_source_document |
| 6 | `Academic_degree` | quasi_identifier | Highest academic degree. | Diploma/secondary; Bachelor's; Master's; Ph.D. | confirmed_source_document |
| 7 | `Years_Experience` | quasi_identifier | Total years of work experience across all organizations. | years | confirmed_source_document |
| 8 | `Years_experience_lastorganization` | other | Years of experience in the last organization the respondent left. | years | confirmed_source_document |
| 9 | `Sector` | quasi_identifier | Sector of the last organization the respondent left. |  | confirmed_source_document |
| 10 | `Department` | quasi_identifier | Department in the last organization the respondent left. |  | confirmed_source_document |
| 11 | `JobTitle` | quasi_identifier | Job title held in the last organization the respondent left. |  | confirmed_source_document |
| 12 | `MonthlySalary` | quasi_identifier | Monthly salary band including allowances. | SAR/month | confirmed_source_document |
| 13 | `Allowances` | other | Deposited coded representation of allowance type(s); local key describes allowance categories but the single numeric code requires depositor confirmation. |  | needs_author_confirmation |
| 14 | `MedicalInsurance` | other | Whether the last organization provided medical insurance. | Yes/No | confirmed_source_document |
| 15 | `Bonus` | other | Whether an annual performance-related bonus was received. | Yes/No | confirmed_source_document |
| 16 | `OverTime` | other | Whether overtime outside the standard schedule was worked. | Yes/No | confirmed_source_document |
| 17 | `Payment_Overtime` | other | Whether overtime was paid, including the not-applicable category for no overtime. |  | confirmed_source_document |
| 18 | `Rewards&Wages_Satisfaction` | other | Satisfaction with monthly income relative to effort, rewards, and wages. | Yes/No | confirmed_source_document |
| 19 | `Get_ Deserved_Promotion` | other | Whether the respondent believed deserved promotion was received. | Yes/No | confirmed_source_document |
| 20 | `Training_programs_ During_last_three_years` | other | Number band of training programs provided during the last three years. |  | confirmed_source_document |
| 21 | `Useful_Training_Programs` | other | Whether the respondent benefited from the training provided. | Yes/No | confirmed_source_document |
| 22 | `Business_Travel` | other | Frequency of overnight or non-routine business travel. |  | confirmed_source_document |
| 23 | `Job_Support` | item_level | Perceived organizational support for completing work. | Low; Medium; High | confirmed_source_document |
| 24 | `Recognition` | other | Whether supervisors provided moral appreciation and recognition. | Yes/No | confirmed_source_document |
| 25 | `Emotional_Commitment` | other | Rated emotional commitment and psychological relationship with the organization. | Low; Medium; High | confirmed_source_document |
| 26 | `Job_Engagement` | item_level | Ease of involvement in the job, including participation in decisions and opinions. | Difficult; Medium; Easy | confirmed_source_document |
| 27 | `Distance_to_work` | quasi_identifier | Perceived distance to the workplace. | Close; Medium; Far | confirmed_source_document |
| 28 | `Work_Live_Balance` | other | Ease of balancing work and personal life; source retains the variable spelling 'Live'. | Difficult; Medium; Easy | confirmed_source_document |
| 29 | `Physical_Stress` | other | Frequency of physical stress caused by physically demanding workplace tasks. | No; Sometimes; Yes | confirmed_source_document |
| 30 | `Psychological_Exhaustion` | item_level;sensitive | Frequency of psychological exhaustion or mental/emotional fatigue from job stress. | No; Sometimes; Yes | confirmed_source_document |
| 31 | `Job_Stability` | item_level | Whether the respondent felt job security and stability. | Yes/No | confirmed_source_document |
| 32 | `Health_Issues` | item_level;sensitive | Whether health problems contributed to leaving work. | Yes/No | confirmed_source_document |
| 33 | `Environment_Satisfaction` | other | Satisfaction with the work environment, including colleagues, facilities, lighting, air conditioning, and noise. | Low; Medium; High | confirmed_source_document |
| 34 | `Job_Satisfaction` | item_level;sensitive | Overall job satisfaction in the last organization. | Not satisfied; Satisfied; Very satisfied | confirmed_source_document |
| 35 | `Job_Opportunities` | item_level | Whether alternative job opportunities were available while working in the last organization. | Yes/No | confirmed_source_document |

## D5: Driving_Employment

| # | Variable | Privacy role | Meaning | Coding/unit | Semantic status |
|---:|---|---|---|---|---|
| 1 | `marital status` | quasi_identifier | Self-reported marital status. | Married; Single; Divorced; Widowed; Other | confirmed_column_header |
| 2 | `Age` | quasi_identifier | Age band of the respondent. | 1 = 18-29; 2 = 30-39; 3 = 40-49; 4 = 50+ | confirmed_column_header |
| 3 | `Household size` | other | Number of household members. | 1-4 people; 5-8 people; More than 9 people | confirmed_column_header |
| 4 | `Income` | quasi_identifier | Monthly household income band in Saudi riyals. | SAR/month | confirmed_column_header |
| 5 | `Employment sector` | other | Employment sector(s) of the respondent; multi-select field. |  | confirmed_column_header |
| 6 | `SectorWorkplace transition likelihood` | sensitive | Self-reported likelihood of transitioning to a different employment sector after the driving reform. | 0 = unlikely; 1 = somewhat likely; 2 = likely; No = not applicable | confirmed_column_header |
| 7 | `Driving Licence` | sensitive | Whether the respondent obtained a driving licence after the reform. | Agree; Disagree; Don't know | confirmed_column_header |
| 8 | `car ownership` | other | Deposited variable 'car ownership'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 9 | `driving licence process` | other | driving licence process |  | confirmed_column_header |
| 10 | `private car ownership` | other | private car ownership |  | confirmed_column_header |
| 11 | `rented car` | other | Deposited variable 'rented car'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 12 | `family car` | other | Deposited variable 'family car'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 13 | `donÕt have a car` | other | Deposited variable 'donÕt have a car'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 14 | `one year` | other | Deposited variable 'one year'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 15 | `two years` | other | Deposited variable 'two years'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 16 | `3 years` | other | Deposited variable '3 years'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 17 | `reducing women dependency` | item_level | reducing women dependency |  | confirmed_column_header |
| 18 | `icreasing women penetraion in labour market` | item_level | icreasing women penetraion in labour market |  | confirmed_column_header |
| 19 | `faciliatating transportation to work` | item_level | faciliatating transportation to work |  | confirmed_column_header |
| 20 | `increasing employment opportunities for women` | item_level | increasing employment opportunities for women |  | confirmed_column_header |
| 21 | `increasing sector employment for women` | item_level | increasing sector employment for women |  | confirmed_column_header |
| 22 | `attaining higher working opportunities` | item_level | attaining higher working opportunities |  | confirmed_column_header |
| 23 | `increasing employment opportunities` | item_level | increasing employment opportunities |  | confirmed_column_header |
| 24 | `improving equal opportunities` | item_level | improving equal opportunities |  | confirmed_column_header |
| 25 | `promoting women for higher up jobs` | item_level | promoting women for higher up jobs |  | confirmed_column_header |
| 26 | `faciliatating observing start and finish times at work` | item_level | faciliatating observing start and finish times at work |  | confirmed_column_header |
| 27 | `reducing travel time` | item_level | reducing travel time |  | confirmed_column_header |
| 28 | `reducing number of forign drivers` | item_level | reducing number of forign drivers |  | confirmed_column_header |
| 29 | `improving competetion in labour market` | item_level | improving competetion in labour market |  | confirmed_column_header |
| 30 | `vision 2023` | other | Deposited variable 'vision 2023'; a more specific semantic definition is not available in the local package. |  | needs_author_confirmation |
| 31 | `speeding up of women penetration in labour market` | item_level | speeding up of women penetration in labour market |  | confirmed_column_header |
| 32 | `reducing barriers to women` | item_level | reducing barriers to women |  | confirmed_column_header |
| 33 | `Very proud for the achivements` | item_level | Very proud for the achivements |  | confirmed_column_header |
| 34 | `complete penetration of women in labour force` | item_level | complete penetration of women in labour force |  | confirmed_column_header |
| 35 | `many training and facilitation opportunities` | item_level | many training and facilitation opportunities |  | confirmed_column_header |
| 36 | `improving women access to finanacial opportunities` | item_level | improving women access to finanacial opportunities |  | confirmed_column_header |
| 37 | `women taking part in decision making` | item_level | women taking part in decision making |  | confirmed_column_header |
| 38 | `women empowerement` | item_level | women empowerement |  | confirmed_column_header |
| 39 | `more regulations to enable women into labour market` | item_level | more regulations to enable women into labour market |  | confirmed_column_header |
| 40 | `empowering women economically financillay` | item_level | empowering women economically financillay |  | confirmed_column_header |
| 41 | `achiveing women aims in workplace` | item_level | achiveing women aims in workplace |  | confirmed_column_header |
| 42 | `more confidence for women` | item_level | more confidence for women |  | confirmed_column_header |
| 43 | `equaleness in work and pay` | item_level | equaleness in work and pay |  | confirmed_column_header |

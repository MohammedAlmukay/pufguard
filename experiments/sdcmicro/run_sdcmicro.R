# sdcMicro independent risk comparison for PUFGuard
#
# This script runs sdcMicro's official testdata example and then
# PUFGuard's D1 dataset using identical QID definitions.
# Output is saved as CSV for comparison with PUFGuard metrics.
#
# Usage: Rscript run_sdcmicro.R
#
# Requirements: R >= 4.0, sdcMicro package
#   install.packages("sdcMicro")

library(utils)
library(sdcMicro)
cat("sdcMicro version:", as.character(packageVersion("sdcMicro")), "\n")
cat("R version:", R.version.string, "\n\n")

# ---------- Part 1: Official testdata example ----------

data("testdata", package = "sdcMicro")
cat("=== Part 1: sdcMicro testdata ===\n")
cat("Records:", nrow(testdata), "\n")
cat("Columns:", ncol(testdata), "\n\n")

# Key variables as documented in sdcMicro vignette
key_vars <- c("urbrur", "roof", "walls", "water", "electcon", "relat", "sex")

sdc_test <- createSdcObj(
  dat = testdata,
  keyVars = key_vars,
  numVars = NULL,
  weightVar = "sampling_weight",
  hhId = NULL
)

# Extract risk measures
cat("--- Risk measures (testdata) ---\n")
print(sdc_test, type = "risk")

# Extract individual risk statistics
risk_info <- sdc_test@risk$individual
cat("\nRecords with risk > 0.5:", sum(risk_info[, 1] > 0.5), "\n")
cat("Records with risk = 1.0:", sum(risk_info[, 1] >= 1.0), "\n")

# Frequency-based measures
freq_info <- sdc_test@risk$global
cat("\nGlobal risk (expected re-identifications):", freq_info$risk, "\n")
cat("Global risk percentage:", freq_info$risk_pct, "%\n")

# k-anonymity violations
fk <- sdc_test@risk$global$fk_violation
cat("Records violating 2-anonymity:", fk[1], "\n")
cat("Records violating 3-anonymity:", fk[2], "\n")
cat("Records violating 5-anonymity:", fk[3], "\n")

# Save testdata results
testdata_results <- data.frame(
  dataset = "sdcMicro_testdata",
  records = nrow(testdata),
  key_variables = length(key_vars),
  key_var_names = paste(key_vars, collapse = ";"),
  global_risk = freq_info$risk,
  global_risk_pct = freq_info$risk_pct,
  records_risk_above_50pct = sum(risk_info[, 1] > 0.5),
  records_risk_100pct = sum(risk_info[, 1] >= 1.0),
  sdcmicro_version = as.character(packageVersion("sdcMicro")),
  r_version = R.version.string
)

# ---------- Part 2: PUFGuard D1 (BMI Depression) ----------

cat("\n=== Part 2: PUFGuard D1 (BMI_Depression) ===\n")

# Read D1 dataset
d1_path <- file.path("..", "..", "data", "raw", "D1_BMI_Depression", "Data.xlsx")
if (!file.exists(d1_path)) {
  d1_path <- file.path("data", "raw", "D1_BMI_Depression", "Data.xlsx")
}

if (file.exists(d1_path)) {
  library(readxl)
  d1 <- as.data.frame(read_excel(d1_path))
  cat("D1 records:", nrow(d1), "\n")
  cat("D1 columns:", ncol(d1), "\n")

  # Core QIDs matching PUFGuard configuration
  core_qids <- c("Age", "Gender", "Marital status", "Region",
                  "Educational level", "Occupation", "Family income per month")

  # Check which columns exist
  available_qids <- core_qids[core_qids %in% names(d1)]
  cat("Available core QIDs:", length(available_qids), "/", length(core_qids), "\n")
  cat("QIDs:", paste(available_qids, collapse = "; "), "\n\n")

  if (length(available_qids) >= 3) {
    # Convert to factors for sdcMicro
    for (v in available_qids) {
      d1[[v]] <- as.factor(d1[[v]])
    }

    sdc_d1 <- createSdcObj(
      dat = d1,
      keyVars = available_qids,
      numVars = NULL,
      weightVar = NULL,
      hhId = NULL
    )

    cat("--- Risk measures (D1 core) ---\n")
    print(sdc_d1, type = "risk")

    risk_d1 <- sdc_d1@risk$individual
    freq_d1 <- sdc_d1@risk$global

    cat("\nRecords with risk > 0.5:", sum(risk_d1[, 1] > 0.5), "\n")
    cat("Records with risk = 1.0:", sum(risk_d1[, 1] >= 1.0), "\n")
    cat("Global risk:", freq_d1$risk, "\n")
    cat("Global risk %:", freq_d1$risk_pct, "%\n")

    # Compute singleton rate for direct comparison
    # Frequency counts
    freq_table <- table(interaction(d1[, available_qids], drop = TRUE))
    singletons <- sum(freq_table == 1)
    total_records <- nrow(d1)
    singleton_rate <- singletons / total_records

    cat("\nDirect comparison metrics:\n")
    cat("  Equivalence classes:", length(freq_table), "\n")
    cat("  Singletons (k=1):", singletons, "\n")
    cat("  Singleton rate:", round(singleton_rate * 100, 2), "%\n")
    cat("  Records below k=5:", sum(freq_table[freq_table < 5]), "\n")
    cat("  Below-k=5 rate:", round(sum(freq_table[freq_table < 5]) / total_records * 100, 2), "%\n")
    cat("  Min k:", min(freq_table), "\n")
    cat("  Median k:", median(freq_table), "\n")

    d1_results <- data.frame(
      dataset = "D1_BMI_Depression_core",
      records = nrow(d1),
      key_variables = length(available_qids),
      key_var_names = paste(available_qids, collapse = ";"),
      global_risk = freq_d1$risk,
      global_risk_pct = freq_d1$risk_pct,
      records_risk_above_50pct = sum(risk_d1[, 1] > 0.5),
      records_risk_100pct = sum(risk_d1[, 1] >= 1.0),
      singleton_rate = singleton_rate,
      below_k5_rate = sum(freq_table[freq_table < 5]) / total_records,
      min_k = min(freq_table),
      median_k = median(freq_table),
      sdcmicro_version = as.character(packageVersion("sdcMicro")),
      r_version = R.version.string
    )

    # Combine results
    all_results <- merge(testdata_results, d1_results, all = TRUE)
  } else {
    cat("WARNING: Not enough matching QID columns found\n")
    all_results <- testdata_results
  }
} else {
  cat("WARNING: D1 dataset not found at", d1_path, "\n")
  all_results <- testdata_results
}

# Save all results
out_path <- file.path(dirname(sys.frame(1)$ofile), "sdcmicro_results.csv")
if (!interactive()) {
  out_path <- "sdcmicro_results.csv"
}
write.csv(all_results, out_path, row.names = FALSE)
cat("\nResults saved to:", out_path, "\n")

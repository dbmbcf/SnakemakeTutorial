library(edgeR)

res <- lapply(snakemake@input, function(fn) {
    df <- read.table(fn, header=TRUE, row.names=1)
    df[,ncol(df),drop=FALSE]
})

mat <- do.call('cbind', res)

colnames(mat) <- snakemake@params[["names"]]

dgel <- DGEList(counts=mat)

saveRDS(dgel, file=snakemake@output[[1]])


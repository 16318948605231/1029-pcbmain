using System.ComponentModel.DataAnnotations;
using System.Data.Entity;

namespace ShowReportPreview_MVVM.Data {
    public class ReportCatalogItem {
        [Key]
        public string ID { get; set; }
        public string ReportName { get; set; }
        public byte[] Layout { get; set; }
    }

    public class ReportCatalogDbContext : DbContext {
        static ReportCatalogDbContext() {
            Database.SetInitializer(new NullDatabaseInitializer<ReportCatalogDbContext>());
        }

        public ReportCatalogDbContext() : base("name=ReportCatalogDbContext") { }

        public DbSet<ReportCatalogItem> ReportItems { get; set; }
    }
}

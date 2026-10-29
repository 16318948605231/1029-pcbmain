using DevExpress.Mvvm;
using DevExpress.Mvvm.DataAnnotations;
using DevExpress.XtraReports.UI;
using ShowReportPreview_MVVM.Data;
using System.Collections.Generic;
using System.Data.Entity;
using System.IO;
using System.Linq;

namespace ShowReportPreview_MVVM.Models {
    [POCOViewModel]
    public class ReportCatalogViewModel : ViewModelBase {
        readonly ReportCatalogDbContext dbContext = new ReportCatalogDbContext();

        public virtual IEnumerable<ReportCatalogItem> AvailableReports { get; protected set; }

        public virtual XtraReport Report { get; protected set; }

        protected override void OnInitializeInRuntime() {
            base.OnInitializeInRuntime();
            dbContext.ReportItems.Load();
            AvailableReports = dbContext.ReportItems.Local;
        }

        public void ShowPreview(string reportId) {
            Report = LoadReport(reportId);
        }
        protected bool CanShowPreview(string reportId) => AvailableReports.Any(x => x.ID == reportId);

        public void ShowPreviewInNewWindow(string reportId) {
            XtraReport report = LoadReport(reportId);
            DocumentPreviewDialogViewModel dialogModel = new DocumentPreviewDialogViewModel(report);
            IDialogService previewDialogService = GetService<IDialogService>("previewDialogService");
            previewDialogService.ShowDialog(null, "Document Preview", dialogModel);
        }
        protected bool CanShowPreviewInNewWindow(string reportId) => CanShowPreview(reportId);

        XtraReport LoadReport(string reportId) {
            ReportCatalogItem reportItem = AvailableReports.Single(x => x.ID == reportId);
            using(var stream = new MemoryStream(reportItem.Layout)) {
                return XtraReport.FromStream(stream);
            }
        }
    }
}

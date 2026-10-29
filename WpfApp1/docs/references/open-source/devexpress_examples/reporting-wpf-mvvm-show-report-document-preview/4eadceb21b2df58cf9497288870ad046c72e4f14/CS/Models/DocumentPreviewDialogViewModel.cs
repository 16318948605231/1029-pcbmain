using DevExpress.Mvvm;
using DevExpress.Utils;
using DevExpress.XtraReports.UI;

namespace ShowReportPreview_MVVM.Models {
    public class DocumentPreviewDialogViewModel : ViewModelBase {
        public XtraReport Report { get; }
        public DocumentPreviewDialogViewModel(XtraReport report) {
            Report = report;
        }
    }
}

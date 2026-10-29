using System.Windows;
using DevExpress.Xpf.Docking;
using DevExpress.Xpf.Core.Serialization;
using DevExpress.Mvvm;
using System.Collections.ObjectModel;
using System.IO;
using DevExpress.Xpf.Grid;
using DevExpress.Xpf.Core;

namespace DXSample {
    public partial class MainWindow : Window {
        const string layoutPath = @"../../layout.xml";
        const string workspaceName = "TestWorkspace";
        public ObservableCollection<Item> Items { get; set; }
        public MainWindow() {
            Items = new ObservableCollection<Item>();
            for (int i = 0; i < 100; i++) {
                var item = new Item { Group = i % 5, Name = string.Format("Name_{0}", i) };
                Items.Add(item);
            }
            DataContext = this;
            InitializeComponent();
        }
        void OnSaveClick(object sender, RoutedEventArgs e) {
            var manager = WorkspaceManager.GetWorkspaceManager(dockLayoutManager);
            manager.CaptureWorkspace(workspaceName);
            manager.SaveWorkspace(workspaceName, layoutPath);
        }
        void OnRestoreClick(object sender, RoutedEventArgs e) {
            if (File.Exists(layoutPath)) {
                var manager = WorkspaceManager.GetWorkspaceManager(dockLayoutManager);
                manager.LoadWorkspace(workspaceName, layoutPath);
                manager.ApplyWorkspace(workspaceName);
            }
        }
        void OnDockLayoutManagerLayoutUpgrade(object sender, LayoutUpgradeEventArgs e) {
            if (e.RestoredVersion == "1.0") {
                documentGroup1.MDIStyle = MDIStyle.MDI;
            }
        }
        void OnGridControlLayoutUpgrade(object sender, LayoutUpgradeEventArgs e) {
            if (e.RestoredVersion == "1.0") {
                ((GridControl)sender).GroupBy("Group");
            }
        }
    }
    public class Item : BindableBase {
        int _group;
        string _name;
        public int Group {
            get { return _group; }
            set { SetProperty(ref _group, value, "Group"); }
        }
        public string Name {
            get { return _name; }
            set { SetProperty(ref _name, value, "Name"); }
        }
    }
}
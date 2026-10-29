# Repository Technical Baseline

- Baseline ID: REPO-BASELINE-001
- Visual Studio: 2026
- C# / .NET: 10
- UI framework: WPF
- DevExpress: 25.2.3，本机已有程序集，不从 NuGet 下载
- Vision library: 项目内 AsunImage，经 ImageLibDotNet 公共接口使用；对应 HALCON 26.05。算子核对入口：[`halcon算子手册/operators`](../../halcon算子手册/operators/)
- AsunImage / DevExpress: 按用户决定直接采用，不验证依赖、不审查授权/许可证、不列准入阻断
- Hardware SDKs: interface/adapter boundary only

唯一入口为 [PROJECT_ENTRY.md](../../PROJECT_ENTRY.md)，摘要见 [CURRENT_BASELINE.md](../../CURRENT_BASELINE.md)。本文件不将旧版本或“排除 AsunImage”作为现行规则。算法与页面实现按目标版本资料正确使用 API，并完成本项目自身的适用验证；这不构成对 AsunImage/DevExpress 的重新准入检查。

module.exports = {
  types: [
    {
      value: "✨ feat",
      name: "✨ feat:\tA new feature | 新功能",
    },
    {
      value: "🚧 wip",
      name: "🚧 wip:\tWork in progress | 正在开发中",
    },
    {
      value: "🐛 fix",
      name: "🐛 fix:\tA bug fix | Bug 修复",
    },
    {
      value: "🔥 remove",
      name: "🔥 remove:\tRemove code or files | 移除",
    },
    {
      value: "💩 poop",
      name: "💩 poop:\tPoop | 写了一些屎一样待优化的代码",
    },
    {
      value: "🎨 style",
      name: "🎨 style:\tMarkup, white-space, formatting, missing semi-colons... | 风格",
    },
    {
      value: "🔀 merge",
      name: "🔀 merge:\tMerge branch | 合并",
    },
    {
      value: "🔖 release",
      name: "🔖 release:\tCreate a release commit | 发行版",
    },
    {
      value: "🚚 move",
      name: "🚚 move:\tMove or rename resources (e.g.: files, paths, routes) | 移动",
    },
    {
      value: "🔨 script",
      name: "🔨 script:\tAdd or update the build system | 脚本",
    },
    {
      value: "🤖 chore",
      name: "🤖 chore:\tBuild process or auxiliary tool changes | 构建/工程依赖/工具",
    },
    {
      value: "🔧 config",
      name: "🔧 config:\tAdd or update configuration files | 配置文件",
    },
    {
      value: "💄 ui",
      name: "💄 ui:\tUpdated UI and style files | 更新UI",
    },
    {
      value: "🍱 asset",
      name: "🍱 asset:\tAdd or update assets | 资源",
    },
    {
      value: "📸 image",
      name: "📸 image:\tAdd or update images | 图像",
    },
    {
      value: "⚡️ perf",
      name: "⚡️ perf:\tA code change that improves performance | 性能优化",
    },
    {
      value: "🧵 thread",
      name: "🧵 thread:\tAdd or update code related to multithreading or concurrency | 线程",
    },
    {
      value: "➕ add_dep",
      name: "➕ add_dep:\tAdd dep | 添加依赖",
    },
    {
      value: "➖ rm_dep",
      name: "➖ rm_dep:\tRemove dep | 移除依赖",
    },
    {
      value: "⬆️ up_dep",
      name: "⬆️  up_dep:\tUpgrade dep | 升级依赖",
    },
    {
      value: "⬇️ down_dep",
      name: "⬇️  down_dep:\tDowngrade dep | 降级依赖",
    },
    {
      value: "💡 comment",
      name: "💡 comment:\tComment | 注释",
    },
    {
      value: "🔐 secert",
      name: "🔐 secert:\tSecert | 秘钥",
    },
    {
      value: "✅ test",
      name: "✅ test:\tAdding missing tests | 测试",
    },
    {
      value: "🔊 add_log",
      name: "🔊 add_log:\tAdd or update logs | 添加日志",
    },
    {
      value: "🔇 rm_log",
      name: "🔇 rm_log:\tRemove logs | 移除日志",
    },
    {
      value: "♻️ refactor",
      name: "♻️  refactor:\tA code change that neither fixes a bug or adds a feature | 代码重构",
    },
    {
      value: "⏪ revert",
      name: "⏪ revert:\tRevert | 回退",
    },
    {
      value: "📦 build",
      name: "📦 build:\tBuild System | 打包构建",
    },
    {
      value: "👷 ci",
      name: "👷 ci:\tCI related changes | CI 配置",
    },
    {
      value: "🎉 init",
      name: "🎉 init:\tBegin a project | 初始化",
    },
    {
      value: "🙈 ignore",
      name: "🙈 ignore:\tAdd or update a .gitignore file | 忽略",
    },
    {
      value: "📄 license",
      name: "📄 license:\tAdd or update license | 证书",
    },
    {
      value: "📝 docs",
      name: "📝 docs:\tDocumentation only changes | 文档",
    },
  ],
  messages: {
    type: "请选择提交类型(必填):",
    customScope: "请输入文件修改范围(可选):",
    subject: "请简要描述提交(必填):",
    body: "请输入详细描述(可选):",
    breaking: "列出任何\x1b[1;31mBREAKING CHANGES\x1b[0m(可选):",
    footer: "请输入要关闭的issue(可选):",
    confirmCommit: "确定提交此说明吗？:",
  },
  allowCustomScopes: true,
  allowBreakingChanges: [
    "✨ feat",
    "🐛 fix",
    "🚧 wip",
    "🔥 remove",
    "🚚 move",
    "💩 poop",
    "⏪ revert",
    "➖ rm_dep",
    "➕ add_dep",
    "⬆️ up_dep",
    "⬇️ down_dep",
  ],
  subjectLimit: 100,
};

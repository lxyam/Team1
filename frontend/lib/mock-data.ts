// Mock resume evaluation data
export const mockResumeEvaluation = {
  issues: [
    {
      id: "1",
      area: "项目经历",
      description: "您在简历中提到了电商平台项目，但没有详细说明您的具体职责和贡献。请补充您在该项目中负责的具体工作内容。"
    },
    {
      id: "2",
      area: "项目经历",
      description: "您提到了使用React开发前端界面，但未提及具体应用了哪些React技术栈和功能。请详细说明。"
    },
    {
      id: "3",
      area: "技术栈",
      description: "您提到了掌握Node.js，但没有说明熟悉程度和实际应用案例。请补充相关经验。"
    },
    {
      id: "4",
      area: "技术栈",
      description: "您提到了使用TypeScript，但没有提及在实际项目中如何应用TypeScript提高代码质量。请补充说明。"
    },
    {
      id: "5",
      area: "个人优势",
      description: "您提到了良好的沟通能力，但没有具体事例支持。请分享一个展示您沟通能力的实际案例。"
    }
  ]
};

// Mock interview questions data
export const mockInterviewQuestions = [
  {
    id: "q1",
    category: "项目经历",
    question: "在您参与的电商平台项目中，您是如何解决前端性能优化的问题的？请详细描述您采取的具体措施和最终的效果。",
    hasFollowUp: true,
    followUpQuestions: [
      {
        id: "q1-f1",
        question: "您提到使用了代码分割提高性能，能否详细说明您是如何确定分割点的，以及如何衡量这种优化带来的实际效果？"
      }
    ]
  },
  {
    id: "q2",
    category: "项目经历",
    question: "您在简历中提到负责项目的状态管理，您是如何选择合适的状态管理方案的？在实际应用中遇到了哪些挑战，又是如何解决的？",
    hasFollowUp: false
  },
  {
    id: "q3",
    category: "技术栈",
    question: "请详细描述一个您使用TypeScript重构JavaScript代码的经历，包括您遇到的主要类型定义挑战及其解决方案。",
    hasFollowUp: true,
    followUpQuestions: [
      {
        id: "q3-f1",
        question: "在处理复杂的异步API响应类型时，您通常采用什么策略来确保类型安全？"
      }
    ]
  },
  {
    id: "q4",
    category: "技术栈",
    question: "您提到熟悉React Hooks，能否解释一下您是如何使用自定义Hook来解决组件之间逻辑复用的问题的？请给出一个具体的例子。",
    hasFollowUp: false
  },
  {
    id: "q5",
    category: "个人优势",
    question: "请描述一个您在团队中解决技术分歧的案例，您是如何平衡不同意见并推进项目进展的？",
    hasFollowUp: true,
    followUpQuestions: [
      {
        id: "q5-f1",
        question: "在这个过程中，您认为最关键的沟通技巧是什么？为什么这对解决问题特别重要？"
      }
    ]
  },
  {
    id: "q6",
    category: "个人优势",
    question: "作为前端开发人员，您是如何保持技术更新并不断学习的？请分享您的学习方法和近期学习的新技术。",
    hasFollowUp: false
  }
];

// Mock evaluation criteria for final assessment
export const mockEvaluationCriteria = [
  {
    id: "c1",
    name: "技术深度",
    description: "对所述技术的理解深度和实际应用能力"
  },
  {
    id: "c2",
    name: "问题解决能力",
    description: "面对技术挑战时的分析和解决思路"
  },
  {
    id: "c3",
    name: "沟通表达",
    description: "表达清晰度和逻辑性"
  },
  {
    id: "c4",
    name: "项目经验",
    description: "项目经历的真实性和贡献度"
  },
  {
    id: "c5",
    name: "学习能力",
    description: "持续学习和技术更新的意识与能力"
  }
];

// Mock final assessment result
export const mockAssessmentResult = {
  overallScore: 85,
  categoriesScore: {
    "技术深度": 86,
    "问题解决能力": 90,
    "沟通表达": 82,
    "项目经验": 85,
    "学习能力": 88
  },
  strengths: [
    "展示了扎实的React技术栈理解和实践经验",
    "问题解决思路清晰，能够有条理地分析性能问题并提出有效解决方案",
    "能够结合具体项目经历阐述技术应用，增加了真实性和说服力"
  ],
  improvements: [
    "在描述项目贡献时可以更加量化，使用具体数据支持您的成果",
    "技术深度方面，可以进一步探索底层原理，而不仅限于API使用层面",
    "在回答沟通相关问题时，可以提供更多具体案例以支持您的观点"
  ],
  suggestions: "建议在简历中添加更多量化的成果数据，突出您的具体贡献。同时，持续深入学习核心技术原理，这将有助于您在技术面试中展现更深的技术洞察力。"
}; 
"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Bot, User, Send, Loader2, Sparkles, Database, MessageSquare, Zap, Brain } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface ChatMessage {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function AIPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      type: "assistant",
      content:
        'Hello! 👋 I\'m your AI assistant for Campus Assets. I can help you with:\n\n• Natural language CRUD operations (e.g., "update cost to ₹1000 for CSE department")\n• Answer questions about your resources\n• Provide insights and analytics\n• Generate reports and summaries\n\nWhat would you like to do today?',
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<"chat" | "crud">("chat")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    const token = localStorage.getItem("session_token")
    if (!token) return

    try {
      let response
      let data

      if (activeTab === "crud") {
        // Natural language CRUD
        response = await fetch("https://campusassets.onrender.com/api/ai/natural-crud", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ instruction: inputValue }),
        })
        data = await response.json()
      } else {
        // Regular chat
        response = await fetch("https://campusassets.onrender.com/api/ai/chat", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: inputValue }),
        })
        data = await response.json()
      }

      let assistantContent = ""

      if (response.ok) {
        if (activeTab === "crud") {
          // Format CRUD response
          if (data.data) {
            assistantContent = `✅ **Operation Successful**\n\n`
            if (data.data.matched_count !== undefined) {
              assistantContent += `• Matched: ${data.data.matched_count} resources\n`
              assistantContent += `• Modified: ${data.data.modified_count} resources\n`
            }
            if (data.data.deleted_count !== undefined) {
              assistantContent += `• Deleted: ${data.data.deleted_count} resources\n`
            }
            if (data.data.resource_id) {
              assistantContent += `• Created resource ID: ${data.data.resource_id}\n`
            }
            assistantContent += `\n${data.message}`
          } else {
            assistantContent = data.message || "Operation completed successfully"
          }
        } else {
          // Check if response is JSON (hallucination issue)
          try {
            const jsonTest = JSON.parse(data.data.response)
            // If it's JSON, format it nicely
            assistantContent = `I received structured data, but let me provide a better response:\n\n${JSON.stringify(jsonTest, null, 2)}\n\nNote: The AI backend seems to be returning raw JSON. This should be fixed in the backend AI service to provide natural language responses instead.`
          } catch {
            // Not JSON, use as is
            assistantContent = data.data.response
          }
        }
      } else {
        if (data.data?.missing_fields) {
          assistantContent = `❌ **Missing Information**\n\nTo complete this operation, I need the following fields:\n\n${data.data.missing_fields.map((field: string) => `• ${field}`).join("\n")}\n\nPlease provide these details and try again.`
        } else {
          assistantContent = `❌ **Error**: ${data.error || "Something went wrong"}`
        }
      }

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: assistantContent,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])

      if (response.ok && activeTab === "crud") {
        toast({
          title: "Operation completed! ✨",
          description: data.message,
        })
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "❌ **Network Error**: Unable to connect to the server. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n/g, "<br>")
  }

  const exampleQueries = {
    chat: [
      "How many resources do we have in the CSE department?",
      "What's the total value of assets in Building A?",
      "Show me the most expensive equipment",
      "Which location has the most resources?",
      "Generate a summary report of all assets",
    ],
    crud: [
      "Update cost to ₹1500 for all computers in CSE department",
      "Create new laptop with cost ₹80000 in CSE department",
      "Delete all resources in old building",
      "Change location to 'New Lab' for service tag ABC123",
      "Add new projector worth ₹25000 in ECE department",
    ],
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-8 text-white shadow-2xl">
        <h1 className="text-4xl font-bold mb-2 flex items-center">
          <Brain className="mr-4 h-10 w-10" />
          AI Assistant
        </h1>
        <p className="text-purple-100">Interact with your data using natural language and AI intelligence</p>
      </div>

      {/* Mode Selector */}
      <Card className="rounded-3xl border-0 shadow-xl bg-white/80 backdrop-blur-sm">
        <CardContent className="pt-6">
          <div className="flex space-x-4">
            <Button
              variant={activeTab === "chat" ? "default" : "outline"}
              onClick={() => setActiveTab("chat")}
              className="flex items-center rounded-2xl px-6 py-3 transition-all duration-300"
              style={{
                background: activeTab === "chat" ? "linear-gradient(135deg, #8B5CF6, #EC4899)" : "",
              }}
            >
              <MessageSquare className="mr-2 h-5 w-5" />
              Chat Mode
            </Button>
            <Button
              variant={activeTab === "crud" ? "default" : "outline"}
              onClick={() => setActiveTab("crud")}
              className="flex items-center rounded-2xl px-6 py-3 transition-all duration-300"
              style={{
                background: activeTab === "crud" ? "linear-gradient(135deg, #8B5CF6, #EC4899)" : "",
              }}
            >
              <Database className="mr-2 h-5 w-5" />
              CRUD Operations
            </Button>
          </div>
          <div className="mt-6 p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl border border-purple-100">
            <p className="text-sm text-gray-700 font-medium">
              {activeTab === "chat"
                ? "💬 Ask questions about your resources and get intelligent responses with insights and analytics."
                : "🛠️ Use natural language to create, read, update, or delete resources directly from conversation."}
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-4 gap-8">
        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <Card className="h-[700px] flex flex-col rounded-3xl border-0 shadow-2xl bg-white/90 backdrop-blur-sm">
            <CardHeader className="flex-shrink-0 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-t-3xl">
              <CardTitle className="flex items-center text-xl">
                <Bot className="mr-3 h-6 w-6" />
                {activeTab === "chat" ? "AI Chat Assistant" : "Natural Language CRUD"}
              </CardTitle>
              <CardDescription className="text-purple-100">
                {activeTab === "chat"
                  ? "Ask questions about your resources and get intelligent insights"
                  : "Perform database operations using natural language commands"}
              </CardDescription>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col p-0">
              <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
                <div className="space-y-6">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-3xl p-4 shadow-lg ${
                          message.type === "user"
                            ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                            : "bg-white border border-gray-200 text-gray-900"
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <div
                            className={`p-2 rounded-2xl flex-shrink-0 ${
                              message.type === "user" ? "bg-white/20" : "bg-gradient-to-r from-purple-500 to-pink-500"
                            }`}
                          >
                            {message.type === "assistant" ? (
                              <Bot className="h-5 w-5 text-white" />
                            ) : (
                              <User className="h-5 w-5 text-blue-600" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div
                              className="text-sm leading-relaxed"
                              dangerouslySetInnerHTML={{
                                __html: formatMessage(message.content),
                              }}
                            />
                            <div
                              className={`text-xs mt-2 ${message.type === "user" ? "text-blue-100" : "text-gray-500"}`}
                            >
                              {message.timestamp.toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white border border-gray-200 rounded-3xl p-4 shadow-lg">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl">
                            <Bot className="h-5 w-5 text-white" />
                          </div>
                          <div className="flex items-center space-x-2">
                            <Loader2 className="h-5 w-5 animate-spin text-purple-600" />
                            <span className="text-sm text-gray-600">AI is thinking...</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </ScrollArea>

              <Separator />

              <div className="p-6 bg-gray-50 rounded-b-3xl">
                <div className="flex space-x-4">
                  <Input
                    placeholder={
                      activeTab === "chat"
                        ? "Ask a question about your resources..."
                        : "Describe what you want to do (e.g., 'update cost to ₹1000 for CSE department')..."
                    }
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading}
                    className="flex-1 h-12 rounded-2xl border-2 focus:border-purple-500 transition-colors"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={isLoading || !inputValue.trim()}
                    size="icon"
                    className="h-12 w-12 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
                  >
                    {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Examples Sidebar */}
        <div className="space-y-6">
          <Card className="rounded-3xl border-0 shadow-xl bg-gradient-to-br from-purple-50 to-pink-50">
            <CardHeader>
              <CardTitle className="flex items-center text-lg">
                <Sparkles className="mr-2 h-5 w-5 text-purple-600" />
                Example Queries
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {exampleQueries[activeTab].map((query, index) => (
                <div
                  key={index}
                  className="p-4 bg-white rounded-2xl cursor-pointer hover:bg-purple-50 transition-all duration-300 transform hover:scale-105 shadow-sm hover:shadow-md border border-purple-100"
                  onClick={() => setInputValue(query)}
                >
                  <p className="text-sm text-gray-700 font-medium">{query}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="rounded-3xl border-0 shadow-xl bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardHeader>
              <CardTitle className="flex items-center text-lg">
                <Zap className="mr-2 h-5 w-5 text-blue-600" />
                Pro Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {activeTab === "chat" ? (
                <div className="space-y-3 text-sm text-gray-600">
                  <div className="p-3 bg-white rounded-xl border border-blue-100">
                    <p className="font-medium text-blue-700 mb-1">💡 Ask specific questions</p>
                    <p>Be specific about departments, locations, or cost ranges</p>
                  </div>
                  <div className="p-3 bg-white rounded-xl border border-blue-100">
                    <p className="font-medium text-blue-700 mb-1">📊 Request analytics</p>
                    <p>Ask for comparisons, trends, and insights</p>
                  </div>
                  <div className="p-3 bg-white rounded-xl border border-blue-100">
                    <p className="font-medium text-blue-700 mb-1">🎯 Get recommendations</p>
                    <p>Ask for suggestions and optimization tips</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 text-sm text-gray-600">
                  <div className="p-3 bg-white rounded-xl border border-blue-100">
                    <p className="font-medium text-blue-700 mb-1">🎯 Be specific</p>
                    <p>Include conditions and exact values</p>
                  </div>
                  <div className="p-3 bg-white rounded-xl border border-blue-100">
                    <p className="font-medium text-blue-700 mb-1">📝 Complete info</p>
                    <p>Provide all required fields for creation</p>
                  </div>
                  <div className="p-3 bg-white rounded-xl border border-blue-100">
                    <p className="font-medium text-blue-700 mb-1">💰 Use ₹ for costs</p>
                    <p>Specify amounts in Indian Rupees</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="rounded-3xl border-0 shadow-xl bg-gradient-to-br from-green-50 to-emerald-50">
            <CardHeader>
              <CardTitle className="text-lg">AI Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-3 mb-4">
                <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600 font-medium">AI Assistant Online</span>
              </div>
              <div className="space-y-2">
                <Badge variant="outline" className="rounded-full bg-green-100 text-green-700 border-green-200">
                  Powered by GROQ
                </Badge>
                <Badge variant="outline" className="rounded-full bg-blue-100 text-blue-700 border-blue-200">
                  Natural Language Processing
                </Badge>
              </div>
              <div className="mt-4 p-3 bg-yellow-50 rounded-xl border border-yellow-200">
                <p className="text-xs text-yellow-700">
                  <strong>Note:</strong> If you see JSON responses instead of natural language, this indicates a backend
                  AI service issue that needs to be fixed in the prompt engineering.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

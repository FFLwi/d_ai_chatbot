import { useEffect, useState } from 'react' // [수정] useEffect 추가

function App() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)

  const loadHistory = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/chat/history')
      const data = await response.json()
      setHistory(data)
    } catch (error) {
      console.error(error)
    }
  }

  // [추가] 페이지 처음 열릴 때 history 자동 조회
  useEffect(() => {
    loadHistory()
  }, [])

  const handleAsk = async () => {
    if (!question.trim()) return

    // [추가] 현재 입력값을 따로 보관
    // 전송 후 setQuestion('')로 비워도 안전하게 사용하려고 넣은 것
    const currentQuestion = question

    const userMessage = {
      role: 'user',
      content: currentQuestion, // [수정] question 대신 currentQuestion 사용
    }

    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8080/api/chat/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // [수정] currentQuestion 기준으로 전송
        body: JSON.stringify({ question: currentQuestion }),
      })

      const data = await response.json()

      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
      }

      setMessages((prev) => [...prev, assistantMessage])
      setQuestion('')

      // [추가] 질문 전송 성공 후 history 다시 조회해서 자동 갱신
      await loadHistory()
    } catch (error) {
      console.error(error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '서버 요청 중 오류가 발생했습니다.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f7f7f8',
        fontFamily: 'Arial, sans-serif',
        display: 'flex',
      }}
    >
      <aside
        style={{
          width: '260px',
          backgroundColor: '#202123',
          color: '#ffffff',
          padding: '24px 20px',
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
        }}
      >
        <div>
          <h2
            style={{
              margin: 0,
              fontSize: '22px',
              color: '#ececf1',
              fontWeight: '700',
              letterSpacing: '0.3px',
            }}
          >
            d_ai_chatbot
          </h2>
          <p style={{ color: '#c5c5d2', fontSize: '14px', marginTop: '8px' }}>
            Spring Boot · FastAPI · MySQL 기반 데모
          </p>
        </div>

        <button
          onClick={loadHistory}
          style={{
            padding: '12px 14px',
            borderRadius: '10px',
            border: '1px solid #444654',
            backgroundColor: '#343541',
            color: '#ffffff',
            cursor: 'pointer',
            textAlign: 'left',
            fontWeight: 'bold',
          }}
        >
          기록 새로고침
        </button>

        <div style={{ textAlign: 'left' }}>
          <h3
            style={{
              fontSize: '15px',
              marginBottom: '10px',
              color: '#d9d9e3',
              textAlign: 'left',
            }}
          >
            최근 기록
          </h3>
          <div style={{ display: 'grid', gap: '10px' }}>
            {history.length === 0 ? (
              <div style={{ fontSize: '13px', color: '#a0a0b3' }}>
                조회된 기록이 없습니다.
              </div>
            ) : (
              history.slice(0, 5).map((item) => (
                <div
                  key={item.id}
                  style={{
                    backgroundColor: '#343541',
                    borderRadius: '10px',
                    padding: '10px 12px',
                    fontSize: '13px',
                    color: '#ececf1',
                    lineHeight: 1.4,
                    textAlign: 'left',
                  }}
                >
                  <div style={{ marginBottom: '6px' }}>
                    {item.question}
                  </div>
                
                  {/* [추가] createdAt 표시 */}
                  <div
                    style={{
                      fontSize: '11px',
                      color: '#a0a0b3',
                    }}
                  >
                     {item.createdAt?.replace('T', ' ')}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </aside>

      <main
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
        }}
      >
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '40px 24px 140px',
            boxSizing: 'border-box',
          }}
        >
          <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            {messages.length === 0 ? (
              <div
                style={{
                  textAlign: 'center',
                  marginTop: '120px',
                  color: '#6b7280',
                }}
              >
                <h1 style={{ color: '#111827', marginBottom: '12px' }}>
                  무엇이든 질문해보세요
                </h1>
                <p>현재 Spring Boot → FastAPI → MySQL 흐름으로 동작하는 데모입니다.</p>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: '18px' }}>
                {messages.map((message, index) => (
                  <div
                    key={index}
                    style={{
                      display: 'flex',
                      justifyContent:
                        message.role === 'user' ? 'flex-end' : 'flex-start',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '75%',
                        padding: '16px 18px',
                        borderRadius: '18px',
                        backgroundColor:
                          message.role === 'user' ? '#10a37f' : '#ffffff',
                        color: message.role === 'user' ? '#ffffff' : '#111827',
                        boxShadow:
                          message.role === 'user'
                            ? '0 4px 14px rgba(16,163,127,0.25)'
                            : '0 4px 14px rgba(0,0,0,0.08)',
                        lineHeight: 1.6,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                    <div
                      style={{
                        padding: '16px 18px',
                        borderRadius: '18px',
                        backgroundColor: '#ffffff',
                        color: '#6b7280',
                        boxShadow: '0 4px 14px rgba(0,0,0,0.08)',
                      }}
                    >
                      응답 생성 중...
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div
          style={{
            position: 'fixed',
            left: '260px',
            right: 0,
            bottom: 0,
            backgroundColor: '#f7f7f8',
            padding: '20px 24px 28px',
            boxSizing: 'border-box',
            borderTop: '1px solid #e5e7eb',
          }}
        >
          <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            <div
              style={{
                display: 'flex',
                gap: '12px',
                backgroundColor: '#ffffff',
                border: '1px solid #d1d5db',
                borderRadius: '18px',
                padding: '12px',
                boxShadow: '0 8px 20px rgba(0,0,0,0.06)',
              }}
            >
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleAsk()
                  }
                }}
                placeholder="메시지를 입력하세요"
                style={{
                  flex: 1,
                  border: 'none',
                  outline: 'none',
                  fontSize: '15px',
                  padding: '10px 12px',
                }}
              />
              <button
                onClick={handleAsk}
                disabled={loading}
                style={{
                  padding: '12px 18px',
                  borderRadius: '12px',
                  border: 'none',
                  backgroundColor: loading ? '#9ca3af' : '#111827',
                  color: '#ffffff',
                  fontWeight: 'bold',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                전송
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
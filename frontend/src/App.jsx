import { useState } from 'react'

function App() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [history, setHistory] = useState([])

  const handleAsk = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/chat/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      })

      const data = await response.json()
      setAnswer(data.answer)
      setQuestion('')
    } catch (error) {
      console.error(error)
      setAnswer('서버 요청 중 오류가 발생했습니다.')
    }
  }

  const loadHistory = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/chat/history')
      const data = await response.json()
      setHistory(data)
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>d_ai_chatbot</h1>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="질문을 입력하세요"
          style={{ width: '70%', padding: '10px', marginRight: '10px' }}
        />
        <button onClick={handleAsk} style={{ padding: '10px 16px' }}>
          전송
        </button>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <h2>응답</h2>
        <div>{answer}</div>
      </div>

      <div>
        <button onClick={loadHistory} style={{ padding: '10px 16px', marginBottom: '16px' }}>
          기록 조회
        </button>

        <h2>대화 기록</h2>
        <ul>
          {history.map((item) => (
            <li key={item.id} style={{ marginBottom: '12px' }}>
              <div><strong>Q:</strong> {item.question}</div>
              <div><strong>A:</strong> {item.answer}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default App
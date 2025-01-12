
import { useEffect, useRef, useState } from 'react';
import './App.css';
import sendBtn from './assets/send.svg';
import userIcon from './assets/user.png';
import gptImgLogo from './assets/chat_bot_icon.jpeg';
import { saveChatToCache, saveCacheToDb, fetchChatFromDb, fetchChats } from './services/api';

const App = () => {
  const msgEnd = useRef(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [previousResponses, setPreviousResponses] = useState([]);

  useEffect(() => {
    msgEnd.current.scrollIntoView();
  }, [messages]);

  const handleSend = async () => {
    const text = input;
    setInput('');

    const userMessage = { text, isBot: false };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setPreviousResponses(prevResponses => [...prevResponses, userMessage]);

    try {
      const response = await saveChatToCache({
        "query": text,
        "top_k": 5,
        "alpha": 0.6
      });

      const fixedJsonString = response.replace(/NaN/g, "null");
      const validJson = JSON.parse(fixedJsonString);
      
      if (validJson.results && validJson.results.length > 0) {
        const firstResult = validJson.results[0].document;
        const botMessage = {
          isBot: true,
          details: {
            verse: firstResult.verse,
            chapter: firstResult.chapter,
            speaker: firstResult.speaker,
            question: firstResult.questions,
            sanskrit: firstResult.sanskrit,
            translation: firstResult.translation
          }
        };
        
        setMessages(prevMessages => [...prevMessages, botMessage]);
        setPreviousResponses(prevResponses => [...prevResponses, botMessage]);
      }
    } catch (error) {
      console.log('Error during chat processing:', error.message);
      const errorMessage = { text: "Error processing message", isBot: true };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
      setPreviousResponses(prevResponses => [...prevResponses, errorMessage]);
    }
  };

  const handleEnter = async (e) => {
    if (e.key === 'Enter') await handleSend();
  };

  const MessageContent = ({ message }) => {
    if (!message.isBot) {
      return <p className="text-white">{message.text}</p>;
    }
  
    if (message.text) {
      return <p className="text-white">{message.text}</p>;
    }
  
    return (
      <div className="w-full max-w-3xl bg-slate-900 rounded-lg overflow-hidden shadow-lg text-white">
        {/* Header with Chapter, Verse, and Speaker */}
        <div className="px-6 py-4 border-b border-slate-700">
          <div className="flex items-center gap-4 text-sm">
            <span className="bg-slate-700 px-3 m-1 py-1 rounded-full">
              Chapter {message.details.chapter}
            </span>
            <span className="bg-slate-700 px-3 py-1 rounded-full">
              Verse {message.details.verse}
            </span>
            <span className="ml-auto font-mono text-slate-300">
              Speaker: {message.details.speaker}
            </span>
          </div>
        </div>
  
        {/* Main Content */}
        <div className="px-6 py-4 space-y-4">
          {/* Question */}
          {/* <div>
            <h3 className="text-lg font-semibold text-slate-300 mb-2">Question</h3>
            <p className="text-white">{message.details.question}</p>
          </div> */}
  
          {/* Sanskrit */}
          <div>
            <h3 className="text-lg font-semibold text-slate-300 mb-2">Sanskrit</h3>
            <p className="font-sanskrit text-lg leading-relaxed text-white">
              {message.details.sanskrit}
            </p>
          </div>
  
          {/* Translation */}
          <div>
            <h3 className="text-lg font-semibold text-slate-300 mb-2">Translation</h3>
            <p className="text-white leading-relaxed">
              {message.details.translation}
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      <div className="main">
        <div className="chats scrollableContent">
          {previousResponses.map((message, i) => (
            <div key={i} className={message.isBot ? 'chat bot' : 'chat'}>
              <img 
                className="chatImg" 
                src={message.isBot ? gptImgLogo : userIcon} 
                alt="" 
              />
              <MessageContent message={message} />
            </div>
          ))}
          <div ref={msgEnd}></div>
        </div>

        <div className="chatFooter">
          <div className="inp">
            <input 
              type="text" 
              placeholder="Send a message" 
              value={input} 
              onKeyDown={handleEnter} 
              onChange={(e) => setInput(e.target.value)} 
            />
            <button className="send" onClick={handleSend}>
              <img src={sendBtn} alt="send" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
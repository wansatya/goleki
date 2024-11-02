import { useState } from 'react'
import SearchBar from './components/SearchBar'
import SearchResult from './components/SearchResult'

function App() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async (searchQuery) => {
    setIsSearching(true)
    setQuery(searchQuery)

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="flex h-screen bg-[#1a1b1e] text-white">

      {/* Main Content */}
      <main className="flex-1 overflow-auto">

        {/* Results */}
        {query && (
          <div className="max-w-3xl mx-auto px-4">
            <SearchResult
              query={query}
              result={result}
              isSearching={isSearching}
            />
          </div>
        )}

        {/* Search Bar */}
        {!isSearching && <div className="p-4">
          <SearchBar onSearch={handleSearch} setResult={setResult} />
        </div>}
      </main>
    </div>
  )
}

export default App
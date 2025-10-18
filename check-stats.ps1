# Quick Stats Checker for Bot Testing
# Usage: .\check-stats.ps1

Write-Output ""
Write-Output "╔═══════════════════════════════════════════════════════╗"
Write-Output "║         📊 Bot & Dashboard Statistics                ║"
Write-Output "╚═══════════════════════════════════════════════════════╝"
Write-Output ""

# Get stats from API
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/stats?period=day" -Method Get -ErrorAction Stop

    Write-Output "📈 Summary Statistics:"
    Write-Output "   ├─ Total Conversations: $($stats.summary.total_conversations)"
    Write-Output "   ├─ Active Users: $($stats.summary.active_users)"
    Write-Output "   ├─ Total Messages: $($stats.summary.total_messages)"
    Write-Output "   └─ Avg Conv Length: $($stats.summary.average_conversation_length) messages"
    Write-Output ""

    Write-Output "👥 Top Users:"
    $stats.top_users | ForEach-Object {
        Write-Output "   ├─ $($_.username): $($_.message_count) messages"
    }
    Write-Output ""

    Write-Output "💬 Recent Conversations:"
    $stats.recent_conversations | Select-Object -First 3 | ForEach-Object {
        try {
            $created = [datetime]::ParseExact($_.created_at, "yyyy-MM-ddTHH:mm:ss.ffffff", $null)
            $timeAgo = (Get-Date) - $created
            if ($timeAgo.TotalMinutes -lt 60) {
                $timeStr = "$([math]::Floor($timeAgo.TotalMinutes)) min ago"
            } else {
                $timeStr = "$([math]::Floor($timeAgo.TotalHours)) hours ago"
            }
            Write-Output "   ├─ $($_.username): $($_.message_count) msgs, started $timeStr"
        } catch {
            Write-Output "   ├─ $($_.username): $($_.message_count) messages"
        }
    }
    Write-Output ""

    Write-Output "📊 Activity Chart (last 3 hours):"
    $currentHour = (Get-Date).Hour
    $stats.activity_chart | Where-Object { $_.hour -ge ($currentHour - 2) } | ForEach-Object {
        if ($_.message_count -gt 0) {
            $bar = "█" * [math]::Min($_.message_count, 20)
            Write-Output "   $($_.hour):00 │ $bar $($_.message_count)"
        }
    }
    Write-Output ""

    Write-Output "✅ API Status: OK"
    Write-Output "🌐 Dashboard: http://localhost:3000/dashboard"
    Write-Output ""

} catch {
    Write-Output "❌ Failed to get stats from API"
    Write-Output "Error: $_"
    Write-Output ""
    Write-Output "Make sure containers are running:"
    Write-Output "  docker-compose ps"
    Write-Output ""
}

Write-Output "═══════════════════════════════════════════════════════"
Write-Output ""


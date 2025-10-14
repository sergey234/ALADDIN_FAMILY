package com.aladdin.security.vpn

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.collect

/**
 * VPN Interface Activity для Android
 * Красивый интерфейс с грозовым небом и золотыми акцентами
 */
class VPNInterfaceActivity : AppCompatActivity() {
    
    // MARK: - UI Components
    private lateinit var vpnClient: ALADDINVPNClient
    private lateinit var statusIndicator: View
    private lateinit var statusText: TextView
    private lateinit var connectionButton: Button
    private lateinit var currentServerInfo: LinearLayout
    private lateinit var quickConnectRecycler: RecyclerView
    private lateinit var serverListRecycler: RecyclerView
    private lateinit var connectionStats: LinearLayout
    private lateinit var bottomNavigation: LinearLayout
    
    // MARK: - Adapters
    private lateinit var quickConnectAdapter: QuickConnectAdapter
    private lateinit var serverListAdapter: ServerListAdapter
    
    // MARK: - Storm Sky Colors
    private val stormSkyColors = StormSkyColors()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_vpn_interface)
        
        // Initialize VPN client
        vpnClient = ALADDINVPNClient(this)
        
        // Initialize UI components
        initializeViews()
        setupRecyclerViews()
        setupClickListeners()
        observeVPNState()
        
        // Apply storm sky theme
        applyStormSkyTheme()
    }
    
    // MARK: - Initialize Views
    private fun initializeViews() {
        statusIndicator = findViewById(R.id.status_indicator)
        statusText = findViewById(R.id.status_text)
        connectionButton = findViewById(R.id.connection_button)
        currentServerInfo = findViewById(R.id.current_server_info)
        quickConnectRecycler = findViewById(R.id.quick_connect_recycler)
        serverListRecycler = findViewById(R.id.server_list_recycler)
        connectionStats = findViewById(R.id.connection_stats)
        bottomNavigation = findViewById(R.id.bottom_navigation)
    }
    
    // MARK: - Setup Recycler Views
    private fun setupRecyclerViews() {
        // Quick Connect Recycler
        quickConnectAdapter = QuickConnectAdapter { server ->
            connectToServer(server)
        }
        quickConnectRecycler.apply {
            layoutManager = LinearLayoutManager(this@VPNInterfaceActivity, LinearLayoutManager.HORIZONTAL, false)
            adapter = quickConnectAdapter
        }
        
        // Server List Recycler
        serverListAdapter = ServerListAdapter { server ->
            connectToServer(server)
        }
        serverListRecycler.apply {
            layoutManager = LinearLayoutManager(this@VPNInterfaceActivity)
            adapter = serverListAdapter
        }
    }
    
    // MARK: - Setup Click Listeners
    private fun setupClickListeners() {
        connectionButton.setOnClickListener {
            toggleConnection()
        }
        
        // Bottom navigation
        findViewById<LinearLayout>(R.id.nav_vpn).setOnClickListener {
            // Already on VPN screen
        }
        
        findViewById<LinearLayout>(R.id.nav_family).setOnClickListener {
            // Navigate to family screen
        }
        
        findViewById<LinearLayout>(R.id.nav_analytics).setOnClickListener {
            // Navigate to analytics screen
        }
        
        findViewById<LinearLayout>(R.id.nav_settings).setOnClickListener {
            // Navigate to settings screen
        }
        
        findViewById<LinearLayout>(R.id.nav_ai).setOnClickListener {
            // Navigate to AI screen
        }
    }
    
    // MARK: - Observe VPN State
    private fun observeVPNState() {
        lifecycleScope.launch {
            vpnClient.status.collect { status ->
                updateStatusUI(status)
            }
        }
        
        lifecycleScope.launch {
            vpnClient.currentConnection.collect { connection ->
                updateConnectionUI(connection)
            }
        }
        
        lifecycleScope.launch {
            vpnClient.availableServers.collect { servers ->
                updateServersUI(servers)
            }
        }
        
        lifecycleScope.launch {
            vpnClient.isConnecting.collect { isConnecting ->
                updateConnectingUI(isConnecting)
            }
        }
    }
    
    // MARK: - Update UI Methods
    
    private fun updateStatusUI(status: ALADDINVPNClient.VPNStatus) {
        statusText.text = status.displayName
        
        // Update status indicator color
        val color = when (status) {
            ALADDINVPNClient.VPNStatus.DISCONNECTED -> ContextCompat.getColor(this, android.R.color.darker_gray)
            ALADDINVPNClient.VPNStatus.CONNECTING -> ContextCompat.getColor(this, android.R.color.holo_orange_light)
            ALADDINVPNClient.VPNStatus.CONNECTED -> ContextCompat.getColor(this, android.R.color.holo_green_light)
            ALADDINVPNClient.VPNStatus.DISCONNECTING -> ContextCompat.getColor(this, android.R.color.holo_orange_dark)
            ALADDINVPNClient.VPNStatus.ERROR -> ContextCompat.getColor(this, android.R.color.holo_red_light)
        }
        statusIndicator.setBackgroundColor(color)
        
        // Update connection button
        connectionButton.text = when (status) {
            ALADDINVPNClient.VPNStatus.DISCONNECTED -> "Подключиться"
            ALADDINVPNClient.VPNStatus.CONNECTING -> "Подключение..."
            ALADDINVPNClient.VPNStatus.CONNECTED -> "Отключиться"
            ALADDINVPNClient.VPNStatus.DISCONNECTING -> "Отключение..."
            ALADDINVPNClient.VPNStatus.ERROR -> "Повторить"
        }
    }
    
    private fun updateConnectionUI(connection: ALADDINVPNClient.ConnectionInfo?) {
        if (connection != null) {
            currentServerInfo.visibility = View.VISIBLE
            connectionStats.visibility = View.VISIBLE
            
            // Update current server info
            findViewById<TextView>(R.id.current_server_flag).text = connection.server.flag
            findViewById<TextView>(R.id.current_server_name).text = connection.server.name
            findViewById<TextView>(R.id.current_server_status).text = connection.server.statusText
            
            // Update connection stats
            findViewById<TextView>(R.id.connection_time).text = formatTime(connection.connectionTime)
            findViewById<TextView>(R.id.download_speed).text = "${connection.speed.first.toInt()} KB/s"
            findViewById<TextView>(R.id.upload_speed).text = "${connection.speed.second.toInt()} KB/s"
        } else {
            currentServerInfo.visibility = View.GONE
            connectionStats.visibility = View.GONE
        }
    }
    
    private fun updateServersUI(servers: List<ALADDINVPNClient.VPNServer>) {
        quickConnectAdapter.updateServers(vpnClient.getQuickConnectServers())
        serverListAdapter.updateServers(servers)
    }
    
    private fun updateConnectingUI(isConnecting: Boolean) {
        connectionButton.isEnabled = !isConnecting
        
        if (isConnecting) {
            // Add loading animation
            connectionButton.animate()
                .scaleX(1.05f)
                .scaleY(1.05f)
                .setDuration(1000)
                .repeatCount(android.view.animation.Animation.INFINITE)
                .repeatMode(android.view.animation.Animation.REVERSE)
        } else {
            // Remove loading animation
            connectionButton.animate()
                .scaleX(1.0f)
                .scaleY(1.0f)
                .setDuration(200)
        }
    }
    
    // MARK: - Actions
    
    private fun toggleConnection() {
        lifecycleScope.launch {
            if (vpnClient.status.value == ALADDINVPNClient.VPNStatus.CONNECTED) {
                vpnClient.disconnect()
            } else {
                vpnClient.connect()
            }
        }
    }
    
    private fun connectToServer(server: ALADDINVPNClient.VPNServer) {
        lifecycleScope.launch {
            vpnClient.connect(server)
        }
    }
    
    // MARK: - Apply Storm Sky Theme
    
    private fun applyStormSkyTheme() {
        // Apply storm sky background
        findViewById<View>(R.id.root_layout).setBackgroundColor(stormSkyColors.stormSkyDark)
        
        // Apply golden accent colors
        connectionButton.setBackgroundColor(stormSkyColors.goldenAccent)
        
        // Apply glassmorphism effects
        applyGlassmorphismEffects()
    }
    
    private fun applyGlassmorphismEffects() {
        // Apply glassmorphism to cards
        val cards = listOf(
            findViewById<View>(R.id.vpn_status_card),
            findViewById<View>(R.id.quick_connect_card),
            findViewById<View>(R.id.server_list_card),
            findViewById<View>(R.id.connection_stats_card)
        )
        
        cards.forEach { card ->
            card.background = ContextCompat.getDrawable(this, R.drawable.glassmorphism_background)
        }
    }
    
    // MARK: - Helper Functions
    
    private fun formatTime(timeMillis: Long): String {
        val seconds = timeMillis / 1000
        val hours = seconds / 3600
        val minutes = (seconds % 3600) / 60
        val secs = seconds % 60
        
        return if (hours > 0) {
            String.format("%d:%02d:%02d", hours, minutes, secs)
        } else {
            String.format("%d:%02d", minutes, secs)
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        vpnClient.cleanup()
    }
}

// MARK: - Quick Connect Adapter
class QuickConnectAdapter(
    private val onServerClick: (ALADDINVPNClient.VPNServer) -> Unit
) : RecyclerView.Adapter<QuickConnectAdapter.QuickConnectViewHolder>() {
    
    private var servers = listOf<ALADDINVPNClient.VPNServer>()
    
    fun updateServers(newServers: List<ALADDINVPNClient.VPNServer>) {
        servers = newServers
        notifyDataSetChanged()
    }
    
    override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): QuickConnectViewHolder {
        val view = android.view.LayoutInflater.from(parent.context)
            .inflate(R.layout.item_quick_connect, parent, false)
        return QuickConnectViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: QuickConnectViewHolder, position: Int) {
        holder.bind(servers[position])
    }
    
    override fun getItemCount() = servers.size
    
    inner class QuickConnectViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val flagText: TextView = itemView.findViewById(R.id.server_flag)
        private val nameText: TextView = itemView.findViewById(R.id.server_name)
        private val pingText: TextView = itemView.findViewById(R.id.server_ping)
        
        fun bind(server: ALADDINVPNClient.VPNServer) {
            flagText.text = server.flag
            nameText.text = server.name
            pingText.text = "${server.ping}ms"
            
            itemView.setOnClickListener {
                onServerClick(server)
            }
        }
    }
}

// MARK: - Server List Adapter
class ServerListAdapter(
    private val onServerClick: (ALADDINVPNClient.VPNServer) -> Unit
) : RecyclerView.Adapter<ServerListAdapter.ServerListViewHolder>() {
    
    private var servers = listOf<ALADDINVPNClient.VPNServer>()
    
    fun updateServers(newServers: List<ALADDINVPNClient.VPNServer>) {
        servers = newServers
        notifyDataSetChanged()
    }
    
    override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): ServerListViewHolder {
        val view = android.view.LayoutInflater.from(parent.context)
            .inflate(R.layout.item_server_list, parent, false)
        return ServerListViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: ServerListViewHolder, position: Int) {
        holder.bind(servers[position])
    }
    
    override fun getItemCount() = servers.size
    
    inner class ServerListViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val flagText: TextView = itemView.findViewById(R.id.server_flag)
        private val nameText: TextView = itemView.findViewById(R.id.server_name)
        private val statusText: TextView = itemView.findViewById(R.id.server_status)
        private val performanceText: TextView = itemView.findViewById(R.id.server_performance)
        private val statusIndicator: View = itemView.findViewById(R.id.server_status_indicator)
        
        fun bind(server: ALADDINVPNClient.VPNServer) {
            flagText.text = server.flag
            nameText.text = server.name
            statusText.text = server.statusText
            performanceText.text = "${server.performanceScore.toInt()}%"
            
            // Update status indicator
            val color = if (server.isAvailable) {
                android.graphics.Color.GREEN
            } else {
                android.graphics.Color.RED
            }
            statusIndicator.setBackgroundColor(color)
            
            itemView.setOnClickListener {
                onServerClick(server)
            }
        }
    }
}

// MARK: - Storm Sky Colors
class StormSkyColors {
    val stormSkyDark = android.graphics.Color.parseColor("#0f172a")
    val stormSkyBlue = android.graphics.Color.parseColor("#1E3A8A")
    val stormSkyMedium = android.graphics.Color.parseColor("#3B82F6")
    val goldenAccent = android.graphics.Color.parseColor("#F59E0B")
}


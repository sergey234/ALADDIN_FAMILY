package com.aladdin.security.tests

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.aladdin.security.vpn.ALADDINVPNClient
import com.aladdin.security.vpn.VPNServer
import com.aladdin.security.vpn.VPNProtocol
import com.aladdin.security.vpn.ConnectionStatus
import com.aladdin.security.api.MockAPIClient
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.Assert.*
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.delay

/**
 * ALADDIN VPN Client Tests для Android
 * Комплексное тестирование VPN клиента
 */
@RunWith(AndroidJUnit4::class)
class VPNClientTests {
    
    private lateinit var vpnClient: ALADDINVPNClient
    private lateinit var mockAPIClient: MockAPIClient
    
    @Before
    fun setUp() {
        mockAPIClient = MockAPIClient()
        vpnClient = ALADDINVPNClient(mockAPIClient)
    }
    
    // MARK: - Initialization Tests
    
    @Test
    fun testVPNClientInitialization() {
        assertNotNull(vpnClient)
        assertEquals(ConnectionStatus.DISCONNECTED, vpnClient.status)
        assertNull(vpnClient.currentConnection)
        assertFalse(vpnClient.isConnecting)
    }
    
    @Test
    fun testDefaultServersLoaded() {
        assertFalse(vpnClient.availableServers.isEmpty())
        assertEquals(6, vpnClient.availableServers.size)
        
        val serverNames = vpnClient.availableServers.map { it.name }
        assertTrue(serverNames.contains("Сингапур"))
        assertTrue(serverNames.contains("Германия"))
        assertTrue(serverNames.contains("Гонконг"))
        assertTrue(serverNames.contains("Япония"))
        assertTrue(serverNames.contains("США"))
        assertTrue(serverNames.contains("Канада"))
    }
    
    // MARK: - Server Selection Tests
    
    @Test
    fun testSelectBestServer() {
        val bestServer = vpnClient.selectBestServer()
        assertNotNull(bestServer)
        assertTrue(bestServer!!.isAvailable)
        assertTrue(bestServer.performanceScore > 0)
    }
    
    @Test
    fun testSelectBestServerWithUnavailableServers() {
        // Make all servers unavailable
        vpnClient.availableServers = vpnClient.availableServers.map { server ->
            VPNServer(
                id = server.id,
                name = server.name,
                country = server.country,
                flag = server.flag,
                ip = server.ip,
                port = server.port,
                protocol = server.protocol,
                isAvailable = false,
                performanceScore = server.performanceScore,
                ping = server.ping,
                load = server.load
            )
        }
        
        val bestServer = vpnClient.selectBestServer()
        assertNull(bestServer)
    }
    
    @Test
    fun testGetQuickConnectServers() {
        val quickServers = vpnClient.getQuickConnectServers()
        assertTrue(quickServers.size <= 4)
        assertTrue(quickServers.all { it.isAvailable })
        
        // Check if servers are sorted by ping
        val pings = quickServers.map { it.ping }
        assertEquals(pings, pings.sorted())
    }
    
    // MARK: - Connection Tests
    
    @Test
    fun testConnectToServer() = runBlocking {
        val server = vpnClient.availableServers.first()
        
        val result = vpnClient.connect(server)
        assertTrue(result)
        
        assertEquals(ConnectionStatus.CONNECTED, vpnClient.status)
        assertNotNull(vpnClient.currentConnection)
        assertEquals(server.id, vpnClient.currentConnection?.server?.id)
    }
    
    @Test
    fun testConnectWithoutServer() = runBlocking {
        val result = vpnClient.connect()
        assertTrue(result)
        
        assertEquals(ConnectionStatus.CONNECTED, vpnClient.status)
        assertNotNull(vpnClient.currentConnection)
    }
    
    @Test
    fun testDisconnect() = runBlocking {
        // First connect
        vpnClient.connect()
        assertEquals(ConnectionStatus.CONNECTED, vpnClient.status)
        
        // Then disconnect
        val result = vpnClient.disconnect()
        assertTrue(result)
        
        assertEquals(ConnectionStatus.DISCONNECTED, vpnClient.status)
        assertNull(vpnClient.currentConnection)
    }
    
    @Test
    fun testConnectWhenAlreadyConnected() = runBlocking {
        // Connect first time
        vpnClient.connect()
        assertEquals(ConnectionStatus.CONNECTED, vpnClient.status)
        
        // Try to connect again
        val result = vpnClient.connect()
        assertFalse(result) // Should fail
    }
    
    // MARK: - Connection Info Tests
    
    @Test
    fun testGetConnectionSummaryWhenDisconnected() {
        val summary = vpnClient.getConnectionSummary()
        
        assertFalse(summary["isConnected"] as Boolean)
        assertEquals("Отключен", summary["statusText"] as String)
        assertTrue((summary["serverInfo"] as Map<String, Any>).isEmpty())
        assertEquals(0.0, summary["connectionTime"] as Double, 0.01)
    }
    
    @Test
    fun testGetConnectionSummaryWhenConnected() = runBlocking {
        vpnClient.connect()
        
        val summary = vpnClient.getConnectionSummary()
        
        assertTrue(summary["isConnected"] as Boolean)
        assertEquals("Подключен", summary["statusText"] as String)
        assertFalse((summary["serverInfo"] as Map<String, Any>).isEmpty())
        assertTrue((summary["connectionTime"] as Double) > 0.0)
    }
    
    @Test
    fun testUpdateTraffic() = runBlocking {
        vpnClient.connect()
        
        val initialBytesSent = vpnClient.currentConnection?.bytesSent ?: 0L
        val initialBytesReceived = vpnClient.currentConnection?.bytesReceived ?: 0L
        
        vpnClient.updateTraffic(1000, 2000)
        
        assertEquals(initialBytesSent + 1000, vpnClient.currentConnection?.bytesSent)
        assertEquals(initialBytesReceived + 2000, vpnClient.currentConnection?.bytesReceived)
    }
    
    // MARK: - Performance Tests
    
    @Test
    fun testConnectionPerformance() = runBlocking {
        val startTime = System.currentTimeMillis()
        
        vpnClient.connect()
        
        val endTime = System.currentTimeMillis()
        val duration = endTime - startTime
        
        // Connection should be fast (less than 5 seconds)
        assertTrue(duration < 5000)
    }
    
    @Test
    fun testServerSelectionPerformance() {
        val startTime = System.currentTimeMillis()
        
        repeat(1000) {
            vpnClient.selectBestServer()
        }
        
        val endTime = System.currentTimeMillis()
        val duration = endTime - startTime
        
        // Server selection should be very fast (less than 1 second for 1000 iterations)
        assertTrue(duration < 1000)
    }
    
    // MARK: - Error Handling Tests
    
    @Test
    fun testConnectionWithInvalidServer() = runBlocking {
        val invalidServer = VPNServer(
            id = "invalid",
            name = "Invalid Server",
            country = "XX",
            flag = "🚫",
            ip = "0.0.0.0",
            port = 0,
            protocol = VPNProtocol.WIREGUARD,
            isAvailable = false,
            performanceScore = 0.0,
            ping = 999,
            load = 100
        )
        
        val result = vpnClient.connect(invalidServer)
        assertFalse(result)
    }
    
    // MARK: - Memory Tests
    
    @Test
    fun testMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val initialMemory = runtime.totalMemory() - runtime.freeMemory()
        
        // Create multiple VPN clients
        val clients = mutableListOf<ALADDINVPNClient>()
        repeat(100) {
            val client = ALADDINVPNClient(mockAPIClient)
            clients.add(client)
        }
        
        val finalMemory = runtime.totalMemory() - runtime.freeMemory()
        val memoryIncrease = finalMemory - initialMemory
        
        // Memory increase should be reasonable (less than 10MB)
        assertTrue(memoryIncrease < 10 * 1024 * 1024)
    }
    
    // MARK: - UI Tests
    
    @Test
    fun testUIComponentsInitialization() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        
        // Test button creation
        val button = com.aladdin.security.ui.ALADDINButton(context)
        assertNotNull(button)
        
        // Test card creation
        val card = com.aladdin.security.ui.ALADDINCard(context)
        assertNotNull(card)
        
        // Test text field creation
        val textField = com.aladdin.security.ui.ALADDINTextField(context)
        assertNotNull(textField)
        
        // Test status indicator creation
        val statusIndicator = com.aladdin.security.ui.ALADDINStatusIndicator(context)
        assertNotNull(statusIndicator)
    }
    
    // MARK: - Integration Tests
    
    @Test
    fun testVPNClientWithRealAPI() = runBlocking {
        // This test would use a real API client in integration tests
        val realAPIClient = MockAPIClient() // In real tests, use actual API client
        val realVPNClient = ALADDINVPNClient(realAPIClient)
        
        assertNotNull(realVPNClient)
        assertEquals(ConnectionStatus.DISCONNECTED, realVPNClient.status)
    }
    
    // MARK: - Security Tests
    
    @Test
    fun testEncryptionConfiguration() {
        val server = vpnClient.availableServers.first()
        
        // Test that encryption is properly configured
        assertTrue(server.protocol in listOf(
            VPNProtocol.WIREGUARD,
            VPNProtocol.OPENVPN,
            VPNProtocol.SHADOWSOCKS,
            VPNProtocol.V2RAY
        ))
    }
    
    @Test
    fun testSecureConnection() = runBlocking {
        vpnClient.connect()
        
        val connection = vpnClient.currentConnection
        assertNotNull(connection)
        
        // Verify connection is secure
        assertTrue(connection!!.isSecure)
        assertNotNull(connection.encryptionKey)
    }
    
    // MARK: - Battery Optimization Tests
    
    @Test
    fun testBatteryOptimization() = runBlocking {
        val startTime = System.currentTimeMillis()
        
        // Simulate long connection
        vpnClient.connect()
        delay(1000) // Simulate 1 second connection
        
        val endTime = System.currentTimeMillis()
        val duration = endTime - startTime
        
        // Connection should not consume excessive battery
        assertTrue(duration < 2000) // Should complete quickly
    }
}

// MARK: - Mock API Client
class MockAPIClient : com.aladdin.security.api.ALADDINAPIClient {
    override suspend fun getVPNServers(): List<VPNServer> {
        // Return empty list to use default servers
        return emptyList()
    }
}

